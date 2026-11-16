# from pathlib import Path
# from typing import Literal

# from fastapi import APIRouter, HTTPException, Request, status
# from fastapi.responses import FileResponse
# from jose import JWTError, jwt
# from sqlalchemy import select
# from core.security import ACCESS, TokenError, decode_token
# from core.config import BASE_DIR
# from core.auth import ALGORITHM
# from core.config import SECRET_KEY
# from db.models.orm import FypGroup, StudentFee, StudentSubmission, TeacherCourse
# from db.session import SessionLocal
# from core.cookies import ROLES, access_name


# router=APIRouter()

# UPLOAD_ROOT=(BASE_DIR / "storage" / "students_uploads").resolve()
# ALLOWED_ROLES={"student","teacher","admin"}




# def get_file_user(request:Request)->dict:
#     token=request.cookies.get("access_token")
#     if not token:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Authentication required")
#     try:
#         return decode_token(token,ACCESS)
#     except TokenError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid or expired token")



# @router.get("/files/{kind}/{record_id}",name="download_private_file")
# def download_private_file(
#     kind: Literal["submission","fyp","voucher"],
#     record_id: int,
#     request: Request,
# ):
#     user=get_file_user(request)
#     role=user["role"]
#     file_path=None
#     allowed=False

#     with SessionLocal() as session:
#         if kind=="submission":
#             record=session.execute(
#                 select(StudentSubmission).where(
#                     StudentSubmission.submission_id==record_id,
#                     StudentSubmission.is_deleted.is_(False),
#                 )
#             ).scalar_one_or_none()

#             if record:
#                 file_path=record.file_path

#                 if role=="admin":
#                     allowed=True
#                 elif role=="student":
#                     allowed=record.student_id==user.get("student_id")
#                 elif role=="teacher":
#                     assigned=session.execute(
#                         select(TeacherCourse.teacher_course_id).where(
#                             TeacherCourse.teacher_id==user.get("teacher_id"),
#                             TeacherCourse.course_id==record.course_id,
#                             TeacherCourse.is_deleted.is_(False),
#                         )
#                     ).first()
#                     allowed=assigned is not None

#         elif kind=="fyp":
#             record=session.execute(
#                 select(FypGroup).where(
#                     FypGroup.fyp_id==record_id,
#                     FypGroup.is_deleted.is_(False),
#                 )
#             ).scalar_one_or_none()

#             if record:
#                 file_path = record.last_submission

#                 if role == "admin":
#                     allowed = True
#                 elif role == "student":
#                     allowed = record.student_id == user.get("student_id")
#                 elif role=="teacher":
#                     allowed=record.teacher_id == user.get("teacher_id")

#         elif kind=="voucher":
#             record=session.execute(
#                 select(StudentFee).where(
#                     StudentFee.student_fees_id==record_id,
#                     StudentFee.is_deleted.is_(False),
#                 )
#             ).scalar_one_or_none()

#             if record:
#                 requested_part=request.query_params.get("part","front")
#                 if requested_part=="front":
#                     file_path=record.voucher_front_pic
#                 elif requested_part=="back":
#                     file_path=record.voucher_back_pic
#                 else:
#                     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid voucher part",)
                    

#                 if role=="admin":
#                     allowed=True
#                 elif role=="student":
#                     allowed=record.student_id==user.get("student_id")

#     if not file_path:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="File not found",)

#     if not allowed:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not allowed to access this file",)

#     try:
#         resolved_path=(UPLOAD_ROOT / file_path).resolve(strict=True)
#         resolved_path.relative_to(UPLOAD_ROOT)
#     except (OSError,ValueError):
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="File not found",)

#     if not resolved_path.is_file():
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="File not found",)

#     return FileResponse(
#         path=resolved_path,
#         filename=resolved_path.name,
#         media_type="application/octet-stream",
#         headers={"Cache-Control":"private, no-store"},
#     )





from typing import Literal

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import FileResponse
from sqlalchemy import select

from core.config import BASE_DIR
from core.cookies import ROLES, access_name
from core.security import ACCESS, TokenError, decode_token
from db.models.orm import FypGroup, StudentFee, StudentSubmission, TeacherCourse
from db.session import SessionLocal


router=APIRouter()

UPLOAD_ROOT=(BASE_DIR / "storage" / "students_uploads").resolve()


def get_file_users(request:Request)->list[dict]:
    """Return every valid logged-in identity found in this browser's cookies."""
    hint=request.query_params.get("role") or request.headers.get("x-role")
    roles=[hint] if hint in ROLES else ["admin","teacher","student"]

    users=[]
    found_token=False
    for role in roles:
        token=request.cookies.get(access_name(role))
        if not token:
            continue
        found_token=True
        try:
            users.append(decode_token(token,ACCESS,expected_role=role))
        except TokenError:
            continue

    if not users:
        detail="Invalid or expired token" if found_token else "Authentication required"
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=detail)
    return users


def _is_allowed(session,user:dict,kind:str,record)->bool:
    role=user.get("role")

    if role=="admin":
        return True

    if kind=="submission":
        if role=="student":
            return record.student_id==user.get("student_id")
        if role=="teacher":
            assigned=session.execute(
                select(TeacherCourse.teacher_course_id).where(
                    TeacherCourse.teacher_id==user.get("teacher_id"),
                    TeacherCourse.course_id==record.course_id,
                    TeacherCourse.is_deleted.is_(False),
                )
            ).first()
            return assigned is not None

    elif kind=="fyp":
        if role=="student":
            return record.student_id==user.get("student_id")
        if role=="teacher":
            return record.teacher_id==user.get("teacher_id")

    elif kind=="voucher":
        if role=="student":
            return record.student_id==user.get("student_id")

    return False


@router.get("/files/{kind}/{record_id}",name="download_private_file")
def download_private_file(
    kind: Literal["submission","fyp","voucher"],
    record_id: int,
    request: Request,
):
    users=get_file_users(request)
    file_path=None
    allowed=False

    with SessionLocal() as session:
        record=None

        if kind=="submission":
            record=session.execute(
                select(StudentSubmission).where(
                    StudentSubmission.submission_id==record_id,
                    StudentSubmission.is_deleted.is_(False),
                )
            ).scalar_one_or_none()
            if record:
                file_path=record.file_path

        elif kind=="fyp":
            record=session.execute(
                select(FypGroup).where(
                    FypGroup.fyp_id==record_id,
                    FypGroup.is_deleted.is_(False),
                )
            ).scalar_one_or_none()
            if record:
                file_path=record.last_submission

        elif kind=="voucher":
            record=session.execute(
                select(StudentFee).where(
                    StudentFee.student_fees_id==record_id,
                    StudentFee.is_deleted.is_(False),
                )
            ).scalar_one_or_none()
            if record:
                requested_part=request.query_params.get("part","front")
                if requested_part=="front":
                    file_path=record.voucher_front_pic
                elif requested_part=="back":
                    file_path=record.voucher_back_pic
                else:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid voucher part")

        if record is not None:
            allowed=any(_is_allowed(session,u,kind,record) for u in users)

    if not file_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="File not found")

    if not allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not allowed to access this file")

    try:
        resolved_path=(UPLOAD_ROOT / file_path).resolve(strict=True)
        resolved_path.relative_to(UPLOAD_ROOT)
    except (OSError,ValueError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="File not found")

    if not resolved_path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="File not found")

    return FileResponse(
        path=resolved_path,
        filename=resolved_path.name,
        media_type="application/octet-stream",
        headers={"Cache-Control":"private, no-store"},
    )