from datetime import date, datetime
from sqlalchemy import select
from core.logger import logging
from db.session import SessionLocal
from db.models.orm import (
    StudentRiskScore,Student,Teacher,TeacherCourse,StudentCourse, RiskIntervention,
)
from modules.risk.trend import get_trends
from datetime import date, datetime, timedelta
from modules.risk.actions import build_actions

TIPS={
    "High":"Please talk to your teacher or advisor soon. Focus on attendance and pending fees first.",
    "Medium":"You are doing okay, but a few areas need attention. Keep an eye on them.",
    "Low":"You are on track. Keep it up!",
}

TEACHER_LABELS={"High":"Needs attention","Medium":"Watch","Low":"On track"}

class RiskReadRepository:
    @staticmethod
    def for_student_user(student_id):
        session=SessionLocal()
        try:
            row=session.execute(
                select(
                    StudentRiskScore.risk_score,
                    StudentRiskScore.risk_level,
                    StudentRiskScore.factors,
                    StudentRiskScore.computed_at,
                )
                .join(Student,Student.student_id==StudentRiskScore.student_id)
                .where(
                    Student.student_id==student_id,
                    Student.is_deleted==False,
                    StudentRiskScore.is_deleted==False,
                    StudentRiskScore.semester==Student.current_semester,
                )
            ).first()
            if not row:
                return None

            trend=get_trends(session,[student_id]).get(student_id)
            reached_out=session.execute(
                select(RiskIntervention.intervention_id).where(
                    RiskIntervention.student_id == student_id,
                    RiskIntervention.is_deleted == False,
                    RiskIntervention.created_at >= datetime.now() - timedelta(days=14),
                ).limit(1)
            ).first() is not None

            try:
                actions=build_actions(session, student_id)
            except Exception as e:
                logging.exception(f"during student actions: {str(e)}")
                actions = []
            return {
                "level":row.risk_level,
                "reasons":row.factors or [],
                "tip":TIPS.get(row.risk_level, ""),
                "computed_at":row.computed_at,
                "trend":trend,
                "reached_out":reached_out,
                "actions":actions,
            }
        except Exception as e:
            logging.exception(f"during student risk: {str(e)}")
            return None      
        finally:
            session.close()

    @staticmethod
    def for_teacher_user(user_id,level=None):
        session=SessionLocal()
        try:
            teacher_id=session.execute(select(Teacher.teacher_id).where(
                    Teacher.user_id==user_id,Teacher.is_deleted==False)).scalar()
            if teacher_id is None:
                return []

            course_ids=session.execute(select(TeacherCourse.course_id).where(
                    TeacherCourse.teacher_id==teacher_id,
                    TeacherCourse.is_deleted==False)).scalars().all()
            
            if not course_ids:
                return []

            student_ids=session.execute(select(StudentCourse.student_id).where(
                    StudentCourse.course_id.in_(course_ids),
                    StudentCourse.is_deleted==False).distinct()).scalars().all()
            
            if not student_ids:
                return []

            stmt=(select(
                    Student.student_id,Student.first_name,Student.last_name,
                    StudentRiskScore.semester,StudentRiskScore.risk_level,
                    StudentRiskScore.factors,)
                .select_from(StudentRiskScore)
                .join(Student,Student.student_id==StudentRiskScore.student_id)
                .where(
                    StudentRiskScore.student_id.in_(student_ids),
                    StudentRiskScore.is_deleted==False,
                    Student.is_deleted==False,
                    StudentRiskScore.semester==Student.current_semester,)
                .order_by(StudentRiskScore.risk_score.desc()))
            
            if level:
                stmt=stmt.where(StudentRiskScore.risk_level==level)

            rows=session.execute(stmt).all()
            trends=get_trends(session,[r.student_id for r in rows])
            statuses = InterventionRepository.status_map(
                session, [r.student_id for r in rows], trends)

            return [
                {
                    "student_id":r.student_id,
                    "name":f"{r.first_name} {r.last_name}",
                    "semester":r.semester,
                    "level":r.risk_level,
                    "label":TEACHER_LABELS.get(r.risk_level,r.risk_level),
                    "reasons":[x for x in (r.factors or []) if "fee" not in x.lower()],
                    "status": statuses[r.student_id],
                    "trend":trends.get(r.student_id),
                }
                for r in rows
            ]
        except Exception as e:
            logging.exception(f"during teacher risk: {str(e)}")
            raise
        finally:
            session.close()  




ACTION_TYPES = ("Spoke", "Warning", "Counseling", "Referred", "Other")

STATUS_LABELS = {
    "none": "No action yet",
    "contacted": "Contacted",
    "overdue": "Follow-up overdue",
    "improving": "Improving",
}


class InterventionRepository:

    @staticmethod
    def _teacher_has_student(session,teacher_id,student_id):
        return session.execute(
            select(StudentCourse.student_course_id)
            .join(TeacherCourse, TeacherCourse.course_id==StudentCourse.course_id)
            .where(
                StudentCourse.student_id==student_id,
                StudentCourse.is_deleted==False,
                TeacherCourse.teacher_id==teacher_id,
                TeacherCourse.is_deleted==False,
            )
        ).first() is not None

    @staticmethod
    def add_note(user_id,role,student_id,action_type,note,follow_up_raw="",teacher_id=None):
        note=(note or "").strip()
        if not note:
            return False, "Please write a short note."
        if len(note) > 500:
            return False, "Note is too long (max 500 characters)."
        if action_type not in ACTION_TYPES:
            return False, "Invalid action type."

        follow_up=None
        if follow_up_raw:
            try:
                follow_up=date.fromisoformat(follow_up_raw)
            except ValueError:
                return False, "Invalid follow-up date."
            if follow_up < date.today():
                return False, "Follow-up date cannot be in the past."

        session=SessionLocal()
        try:
            exists=session.execute(
                select(Student.student_id).where(
                    Student.student_id==student_id,Student.is_deleted==False)
            ).scalar()
            if exists is None:
                return False, "Student not found."

            
            if role=="teacher" and not InterventionRepository._teacher_has_student(session,teacher_id, student_id):
                return False, "You can only add notes for students in your courses."

            session.add(RiskIntervention(
                student_id=student_id,created_by_user_id=user_id,created_by_role=role,
                action_type=action_type,note=note,follow_up_date=follow_up,))
            session.commit()
            return True, "Note saved."
        except Exception as e:
            session.rollback()
            logging.exception(f"during add risk note: {str(e)}")
            return False, "Could not save the note. Try again."
        finally:
            session.close()


    @staticmethod
    def status_map(session,student_ids,trends=None):
        trends=trends or {}
        result={
            sid:{
                "code":"none",
                "label":STATUS_LABELS["none"],
                "last_note":None,
                  "last_at":None,
                  "follow_up":None,
                  "days_since":None,
                  "count": 0}
            for sid in student_ids
        }
        if not student_ids:
            return result

        rows=session.execute(
            select(
                RiskIntervention.student_id,RiskIntervention.note,
                RiskIntervention.created_at,RiskIntervention.follow_up_date,
            )
            .where(RiskIntervention.student_id.in_(student_ids),
                   RiskIntervention.is_deleted==False)
            .order_by(RiskIntervention.student_id,
                      RiskIntervention.created_at.desc(),
                      RiskIntervention.intervention_id.desc())
        ).all()

        today=date.today()
        for r in rows:
            st=result[r.student_id]
            st["count"] += 1
            if st["count"] > 1:          
                continue
            st["last_note"]=r.note
            st["last_at"]=r.created_at
            st["follow_up"]=r.follow_up_date
            st["days_since"]=(today - r.created_at.date()).days if r.created_at else None
            if r.follow_up_date and r.follow_up_date < today:
                code="overdue"
            else:
                code="contacted"

            trend=trends.get(r.student_id)
            if code=="contacted" and trend and trend["direction"]=="better":
                code="improving"

            st["code"]=code
            st["label"]=STATUS_LABELS[code]
        return result
