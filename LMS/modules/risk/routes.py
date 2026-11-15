from fastapi import APIRouter,Depends,HTTPException,Request,Query
from core.auth import get_chat_user
from db.session import get_db
from db.models.orm import (StudentRiskScore,Student,Teacher,TeacherCourse,StudentCourse,)
from .service import compute_and_save,load_model

router=APIRouter()


def _uid(user:dict):
    return user.get("user_id")    


def get_staff(request:Request)->dict:
    user=get_chat_user(request)                    
    if user.get("role") not in ("teacher","admin"):
        raise HTTPException(status_code=403,detail="forbidden")
    
    return user


def get_admin_api(request:Request)->dict:
    user=get_chat_user(request)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403,detail="forbidden")
    
    return user


def get_student_api(request:Request)->dict:
    user=get_chat_user(request)
    if user.get("role") != "student":
        raise HTTPException(status_code=403,detail="forbidden")
    
    return user


def _serialize(r:StudentRiskScore,s:Student)->dict:
    return {
        "student_id":s.student_id,
        "name":f"{s.first_name} {s.last_name}",
        "semester":r.semester,
        "score":float(r.risk_score),
        "level":r.risk_level,
        "reasons":r.factors or [],
    }


@router.get("/api/students")
def at_risk_students(
    level:str | None=Query(None,pattern="^(Low|Medium|High)$"),
    limit:int=Query(100,le=200),
    offset:int=Query(0,ge=0),db=Depends(get_db),user=Depends(get_staff),
):
    q=(
        db.query(StudentRiskScore,Student)
        .join(Student,Student.student_id==StudentRiskScore.student_id)
        .filter(
            StudentRiskScore.is_deleted==False,
            Student.is_deleted==False,
            StudentRiskScore.semester==Student.current_semester, 
        )
    )
    if level:
        q=q.filter(StudentRiskScore.risk_level==level)

    
    if user.get("role")=="teacher":
        teacher_id=(
            db.query(Teacher.teacher_id)
            .filter(Teacher.user_id == _uid(user),Teacher.is_deleted == False)
            .scalar()
        )
        if teacher_id is None:
            return []
        
        course_ids=[c for (c,) in db.query(TeacherCourse.course_id).filter(
            TeacherCourse.teacher_id==teacher_id, TeacherCourse.is_deleted==False)]
        
        student_ids=[s for (s,) in db.query(StudentCourse.student_id).filter(
            StudentCourse.course_id.in_(course_ids), StudentCourse.is_deleted == False).distinct()]
        
        if not student_ids:
            return []
        
        q=q.filter(StudentRiskScore.student_id.in_(student_ids))

    rows=(q.order_by(StudentRiskScore.risk_score.desc()).offset(offset).limit(limit).all())
    return [_serialize(r, s) for r, s in rows]


@router.get("/api/me")
def my_risk(db=Depends(get_db),user=Depends(get_student_api)):
    student=(db.query(Student)
        .filter(Student.user_id == _uid(user), Student.is_deleted == False)
        .first()
    )
    if not student:
        raise HTTPException(status_code=404,detail="student not found")
    
    row=(
        db.query(StudentRiskScore)
        .filter(StudentRiskScore.student_id==student.student_id,
                StudentRiskScore.semester==student.current_semester,
                StudentRiskScore.is_deleted==False)
        .first())
    
    if not row:
        return {
            "level":None,
            "reasons":[]
            }
    
    return {
            "level":row.risk_level,
            "score":float(row.risk_score),
            "reasons":row.factors or []
            }


@router.post("/api/recompute")
def recompute(db=Depends(get_db),user=Depends(get_admin_api)):
    newly_high=compute_and_save(db,model=load_model())
    return {
        "newly_high":len(newly_high)
        }