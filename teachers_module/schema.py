from pydantic import BaseModel, Field,validator,EmailStr
from typing import Optional,List,Dict,List
from datetime import datetime,date


class TeacherLoginRequest(BaseModel):
    email:EmailStr
    password:str
    remember_me:bool=False



class MarkedAttendance(BaseModel):
    section_id:int=Field(...,gt=0)


class AttendanceForm(BaseModel):
    attendance_date:date
    status_record:Dict[str,str]


class ClassStructure(BaseModel):
    section_id:int=Field(...,gt=0)


class GenerateResultPath(BaseModel):
    section_id:int=Field(...,gt=0)

class GenerateResult(BaseModel):
    student_marks:Dict[str,int]


class ApproveFyp(BaseModel):
    fyp_id:int=Field(...,gt=0)
    status:str=Field(...)

class SendMessagePath(BaseModel):
    fyp_id:int=Field(...,gt=0)


class SendMessageForm(BaseModel):
    message:str=Field(...,min_length=1)


class ViewSubmissionPath(BaseModel):
    section_id:int=Field(...,gt=0)
    sub_type:str=Field(...)


class MarkSubmissionPath(BaseModel):
    submission_id:int=Field(...,gt=0)


class MarkSubmissionForm(BaseModel):
    marks:float=Field(...,gt=0)
    total_marks:float=Field(...,gt=0)
    section_id:int=Field(...,gt=0)
    sub_type:str


class ToggleUploadPath(BaseModel):
    section_id:int=Field(...,gt=0)
    upload_type:str=Field(...)


class SetSubmissionStatusPath(BaseModel):
    submission_id:int=Field(...,gt=0)
    status:str=Field(...)


class SetSubmissionStatusForm(BaseModel):
    section_id:int=Field(...,gt=0)
    sub_type:str


class ComplaintSuggestionForm(BaseModel):
    title:str=Field(...,min_length=3,max_length=255)
    description:str=Field(...,min_length=5)
                        
