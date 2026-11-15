from sqlalchemy import func, case
from db.models.orm import (
    Student,StudentCourse,Attendance,StudentResult,
    StudentFailSubject,StudentFee,StudentSubmission,SemesterFreezeStudent,
)

FEATURE_NAMES=["attendance_pct","prev_gpa","gpa_trend",
                 "fail_count","fee_due_count","assignment_avg","freeze_count"]


def build_features(db,student_ids=None)->dict[int,dict]:
    q=db.query(Student.student_id,Student.current_semester).filter(Student.is_deleted==False)
    if student_ids:
        q=q.filter(Student.student_id.in_(student_ids))

    students=q.all()
    ids=[s.student_id for s in students]

    feats={
        s.student_id:{
            "semester":s.current_semester or 1,
            "attendance_pct":None,
            "prev_gpa":None,
            "gpa_trend":0.0,
            "fail_count":0,
            "fee_due_count":0,
            "assignment_avg":None,
            "freeze_count":0,
        } for s in students
    }
    if not ids:
        return feats

    
    rows=(
        db.query(StudentCourse.student_id,func.count(Attendance.attendance_id),
            func.sum(case((Attendance.attendance_status=="Present", 1),else_=0)),
        )
        .join(Attendance,Attendance.student_course_id==StudentCourse.student_course_id)
        .filter(StudentCourse.student_id.in_(ids),
                StudentCourse.is_deleted==False,
                Attendance.is_deleted==False)
        .group_by(StudentCourse.student_id).all()
    )
    for sid,total,present in rows:
        if total:
            feats[sid]["attendance_pct"]=round(float(present or 0) * 100 / total, 1)

    
    gpas={}
    for sid, gpa in (
        db.query(StudentResult.student_id,StudentResult.overall_gpa)
        .filter(StudentResult.student_id.in_(ids),StudentResult.is_deleted == False)
        .order_by(StudentResult.student_id,StudentResult.student_semester).all()
    ):
        gpas.setdefault(sid, []).append(float(gpa))
    for sid, g in gpas.items():
        feats[sid]["prev_gpa"]=g[-1]
        feats[sid]["gpa_trend"]=round(g[-1] - g[-2], 2) if len(g) > 1 else 0.0

   
    for sid,n in (
        db.query(StudentFailSubject.student_id,func.count())
        .filter(StudentFailSubject.student_id.in_(ids),StudentFailSubject.is_deleted == False)
        .group_by(StudentFailSubject.student_id).all()
    ):
        feats[sid]["fail_count"]=n

   
    for sid,n in (
        db.query(StudentFee.student_id,func.count())
        .filter(StudentFee.student_id.in_(ids),StudentFee.fee_status=="due",
                StudentFee.is_deleted==False)
        .group_by(StudentFee.student_id).all()
    ):
        feats[sid]["fee_due_count"]=n

    
    for sid,avg in (
        db.query(StudentSubmission.student_id,
                func.avg(StudentSubmission.marks * 100.0 / StudentSubmission.total_marks))
        .filter(StudentSubmission.student_id.in_(ids),
                StudentSubmission.marks.isnot(None),
                StudentSubmission.total_marks > 0,
                StudentSubmission.is_deleted == False)
        .group_by(StudentSubmission.student_id).all()
    ):
        feats[sid]["assignment_avg"]=round(float(avg), 1)

   
    for sid,n in (
        db.query(SemesterFreezeStudent.student_id, func.count())
        .filter(SemesterFreezeStudent.student_id.in_(ids),
                SemesterFreezeStudent.status=="Approved",
                SemesterFreezeStudent.is_deleted==False)
        .group_by(SemesterFreezeStudent.student_id).all()
    ):
        feats[sid]["freeze_count"]=n

    return feats