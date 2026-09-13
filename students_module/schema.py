from pydantic import BaseModel, Field,validator,EmailStr
from typing import Optional,List
from datetime import datetime



class StudentLoginRequest(BaseModel):
    email:EmailStr
    password:str
    remember_me:bool=False



class LoginResponse(BaseModel):
    success:bool
    message:str
    student_id:int
    user_id:int
    student_name:str




class StudentProfileHelper(BaseModel):
    student_id:int
    user_id:int
    first_name:str
    last_name:str
    email:str
    current_semester:int
    program_id:int

    class Config:
        from_attributes=True


class ProgramDetailHelper(BaseModel):
    program_id:int
    program_name:str
    program_coordinator:str


class StudentProfileResponse(BaseModel):
    student:StudentProfileHelper
    program:ProgramDetailHelper
    show_notification:bool


class CourseHelper(BaseModel):
    course_id:int
    course_name:str
    credit_hours:int
    semester:Optional[int]=None


class TeacherHelper(BaseModel):
    teacher_id:int
    first_name:str
    last_name:str
    email:Optional[str]=None
    contact_num:Optional[str]=None


class CourseScheduleHelper(BaseModel):
    course_schedule_id:int
    course_id:int
    section_id:int
    day:str
    start_time:str
    end_time:str
    room_number:Optional[str]=None
    assignments_enabled:bool=False
    quizzes_enabled:bool=False


class StudentDashboardResponse(BaseModel):
    student_id:int
    student_name:str
    current_semester:int
    enrolled_courses:List[CourseHelper]
    teachers:List[TeacherHelper]
    active_notifications:int
    has_upcoming_exams:bool
    exam_data:Optional[dict]=None


class CourseRegsterationRequest(BaseModel):
    course_id:int
    semester:int

    @validator('course_id')
    def validate_course_id(cls,v):
        if v<1:
            raise ValueError('course_id must be positive')
        return v



class SubmissionHelper(BaseModel):
    submission_id:Optional[int]=None
    course_id:int
    section_id:int
    submission_type:str
    marks:Optional[float]=None
    total_marks:Optional[float]=None
    uploaded_date:Optional[datetime]=None
    file_path:Optional[str]=None


class UploadSubmissionRequest(BaseModel):
    course_id:int
    section_id:int
    submission_type:str

    @validator('submission_type')
    def validate_submission_type(cls,v):
        if v not in ['assignment','quiz']:
            raise ValueError('submission must be assignment or quiz')
        return v


class UploadResponse(BaseModel):
    success:bool
    message:str
    submission_id:Optional[int]=None
    file_size:Optional[int]=None



class SubmissionListResponse(BaseModel):
    total_submissions:int
    uploaded_assignments:List[SubmissionHelper]
    uploaded_quizes:List[SubmissionHelper]



class FYPHelper(BaseModel):
    fyp_id:int
    project_title:str
    description:Optional[str]=None
    student_id:int
    teacher_id:Optional[int]=None
    status:str
    progress:int=Field(ge=0,le=100)


class FYPMessageHelper(BaseModel):
    message_id:int
    fyp_id:int
    sender_role:str
    message:str
    created_at:datetime

class SubmitFYPResponse(BaseModel):
    success:bool
    message:str
    fyp_id:int
    status:str

class FYPDetailResponse(BaseModel):
    fyp:Optional[FYPHelper]=None
    message:List[FYPMessageHelper]=[]
    teacher:Optional[TeacherHelper]=None
    all_teachers:List[TeacherHelper]=[]



class SendFYPMessageRequest(BaseModel):
    message:str=Field(...,min_length=1,max_length=100)



class AttendanceRecordHelper(BaseModel):
    attendance_date:datetime
    attendance_status:str


class CourseAttendanceHelper(BaseModel):
    course_name:str
    credit_hours:int
    total_lectures:int
    attended_lectures:int
    percentage:float
    lecture_status:List[AttendanceRecordHelper]
    teacher_name:str


class AttendanceReportResponse(BaseModel):
    student_id:int
    total_courses:int
    attendance_report:List[CourseAttendanceHelper]


class GradeHelper(BaseModel):
    semester:int
    course_name:str
    credit_hours:int
    total_marks:float
    subject_gpa:float
    status:str



class GradesResponse(BaseModel):
    student_id:int
    student_name:str
    total_semester:int
    all_marks:List[GradeHelper]
    overall_cgpa:float


class FeeRecordHelper(BaseModel):
    program:str
    month:str
    fee_amount:float
    paid_date:datetime
    status:str
    front_voucher:str
    back_voucher:str



class StudentFeeResponse(BaseModel):
    student_id:int
    program:str
    total_fees_due:float
    fees_paid:float
    pending_fees:float
    fee_records:List[FeeRecordHelper]


class UploadFeeVoucherRequest(BaseModel):
    month:str=Field(...,description="Month name or number")
    fee_amount:float=Field(...,gt=0,description="Fee amount")


class UploadFeeResponse(BaseModel):
    success:bool
    message:str
    fee_status:str
    next_payment_due:Optional[str]=None



class ImprovementSubjectHelper(BaseModel):
    improvement_id:int
    course_id:int
    course_name:str
    status:str
    type:str="improvement"


class RetakeSubjectHelper(BaseModel):
    failed_id:int
    course_id:int
    course_name:str
    status:str
    type:str="retake"


class SelectImprovementRequest(BaseModel):
    course_id:int

    @validator('course_id')
    def validate_course_id(cls,v):
        if v<1:
            raise ValueError('course id muust be positive')
        return v


class SelectImprovementResponse(BaseModel):
    success:bool
    message:str
    improvement_id:int


class ImprovementListResponse(BaseModel):
    available_courses:List[CourseHelper]
    existing_improvements:List[ImprovementSubjectHelper]
    can_select:bool


class SemesterFreezeRequest(BaseModel):
    reason:str=Field(...,min_length=10,max_length=1000) 


class SemesterFreezeResponse(BaseModel):
    success:bool
    message:str
    freeze_id:Optional[int]=None
    status:str


class  ComplaintSuggestionRequest(BaseModel):
    title:str=Field(...,min_length=5,max_length=200)
    description:str=Field(...,min_length=10,max_length=2000)



class ComplaintResponse(BaseModel):
    success:bool
    message:str
    complaint_id:int
    status:str



class NotificationHelper(BaseModel):
    id:int
    title:str
    description:str
    created_at:datetime
    status:str


class NotificationResponse(BaseModel):
    total_notifications:int
    active_notifications:List[NotificationHelper]
    unread_count:int




class ErrorResponse(BaseModel):
    success:bool=False
    message:str
    error_code:Optional[str]=None
    detail:Optional[dict]=None


class SuccessResponse(BaseModel):
    success:bool=True
    message:str
    data:Optional[dict]=None







            

        