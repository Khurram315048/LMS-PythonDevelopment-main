from pathlib import Path
from typing import Literal

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import FileResponse
from jose import JWTError, jwt
from sqlalchemy import select
from core.security import ACCESS, TokenError, decode_token
from core.config import BASE_DIR
from core.auth import ALGORITHM
from core.config import SECRET_KEY
from db.models.orm import FypGroup, StudentFee, StudentSubmission, TeacherCourse
from db.session import SessionLocal

router=APIRouter()

UPLOAD_ROOT=(BASE_DIR / "storage" / "students_uploads").resolve()
ALLOWED_ROLES={"student","teacher","admin"}


# def get_file_user(request:Request) -> dict:
#     token=request.cookies.get("access_token")
#     if not token:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Authentication required",
#         )

#     try:
#         user = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#     except JWTError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid or expired token",
#         )

#     if user.get("role") not in ALLOWED_ROLES:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Access denied",
#         )

#     return user


def get_file_user(request:Request) -> dict:
    token=request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Authentication required")
    try:
        return decode_token(token,ACCESS)
    except TokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid or expired token")



@router.get("/files/{kind}/{record_id}",name="download_private_file")
def download_private_file(
    kind: Literal["submission","fyp","voucher"],
    record_id: int,
    request: Request,
):
    user = get_file_user(request)
    role = user["role"]
    file_path = None
    allowed = False

    with SessionLocal() as session:
        if kind == "submission":
            record = session.execute(
                select(StudentSubmission).where(
                    StudentSubmission.submission_id == record_id,
                    StudentSubmission.is_deleted.is_(False),
                )
            ).scalar_one_or_none()

            if record:
                file_path = record.file_path

                if role == "admin":
                    allowed = True
                elif role == "student":
                    allowed = record.student_id == user.get("student_id")
                elif role == "teacher":
                    assigned = session.execute(
                        select(TeacherCourse.teacher_course_id).where(
                            TeacherCourse.teacher_id == user.get("teacher_id"),
                            TeacherCourse.course_id == record.course_id,
                            TeacherCourse.is_deleted.is_(False),
                        )
                    ).first()
                    allowed = assigned is not None

        elif kind == "fyp":
            record = session.execute(
                select(FypGroup).where(
                    FypGroup.fyp_id == record_id,
                    FypGroup.is_deleted.is_(False),
                )
            ).scalar_one_or_none()

            if record:
                file_path = record.last_submission

                if role == "admin":
                    allowed = True
                elif role == "student":
                    allowed = record.student_id == user.get("student_id")
                elif role == "teacher":
                    allowed = record.teacher_id == user.get("teacher_id")

        elif kind == "voucher":
            record = session.execute(
                select(StudentFee).where(
                    StudentFee.student_fees_id == record_id,
                    StudentFee.is_deleted.is_(False),
                )
            ).scalar_one_or_none()

            if record:
                # A fee record can contain two separately saved voucher paths.
                requested_part = request.query_params.get("part", "front")
                if requested_part == "front":
                    file_path = record.voucher_front_pic
                elif requested_part == "back":
                    file_path = record.voucher_back_pic
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid voucher part",
                    )

                if role == "admin":
                    allowed = True
                elif role == "student":
                    allowed = record.student_id == user.get("student_id")

    if not file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to access this file",
        )

    # Resolve the database-stored relative path under the uploads directory.
    # This rejects traversal and symlinks that point outside the upload root.
    try:
        resolved_path = (UPLOAD_ROOT / file_path).resolve(strict=True)
        resolved_path.relative_to(UPLOAD_ROOT)
    except (OSError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    if not resolved_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    return FileResponse(
        path=resolved_path,
        filename=resolved_path.name,
        media_type="application/octet-stream",
        headers={"Cache-Control": "private, no-store"},
    )