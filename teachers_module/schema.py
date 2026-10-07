from pydantic import BaseModel, Field,model_validator,EmailStr,ConfigDict
from typing import Optional,List,Dict,List,Any,Literal
from datetime import datetime,date


subType=Literal['assignment','quiz']
subStatus=Literal['Best','Average','Worst']
FypStatus=Literal['Approved','Rejected','Completed']


class TeacherLoginRequest(BaseModel):
    email:EmailStr
    password:str
    remember_me:bool=False



# class MarkedAttendance(BaseModel):
#     section_id:int=Field(...,gt=0)


class AttendanceForm(BaseModel):
    attendance_date:date
    status_record:Dict[int,Literal['Present','Absent']]

    @model_validator(mode='after')
    def check_format(self):
        if not self.status_record:
            raise ValueError("No attendance found")
        if self.attendance_date>date.today():
            raise ValueError("Attendance date cannot exceed")
        
        return self


# class ClassStructure(BaseModel):
#     section_id:int=Field(...,gt=0)


# class GenerateResultPath(BaseModel):
#     section_id:int=Field(...,gt=0)

# class GenerateResult(BaseModel):
#     student_marks:Dict[str,Any]

#     @model_validator(mode='after')
#     def validate_results(self):
#         sessional={k: v for k,v in self.student_marks.items() if k.startswith('sessional_')}
#         if not sessional:
#             raise ValueError("No result found")

#         return self
    


# class ApproveFyp(BaseModel):
#     fyp_id:int=Field(...,gt=0)
#     status:str=Field(...)

# class SendMessagePath(BaseModel):
#     fyp_id:int=Field(...,gt=0)


class SendMessageForm(BaseModel):
    model_config=ConfigDict(str_strip_whitespace=True)
    message:str=Field(...,min_length=1,max_length=2000)


# class ViewSubmissionPath(BaseModel):
#     section_id:int=Field(...,gt=0)
#     sub_type:str=Field(...)


# class MarkSubmissionPath(BaseModel):
#     submission_id:int=Field(...,gt=0)


class MarkSubmissionForm(BaseModel):
    marks:int=Field(...,ge=0)
    total_marks:int=Field(...,gt=0)
    section_id:int=Field(...,gt=0)
    sub_type:subType

    @model_validator(mode='after')
    def check_marks(self):
        if self.marks>self.total_marks:
            raise ValueError("Obtained marks cannot be grater than total marks")

        return self


# class ToggleUploadPath(BaseModel):
#     section_id:int=Field(...,gt=0)
#     upload_type:str=Field(...)


# class SetSubmissionStatusPath(BaseModel):
#     submission_id:int=Field(...,gt=0)
#     status:str=Field(...)


# class SetSubmissionStatusForm(BaseModel):
#     section_id:int=Field(...,gt=0)
#     sub_type:str


class ComplaintSuggestionForm(BaseModel):
    model_config=ConfigDict(str_strip_whitespace=True)
    title:str=Field(...,min_length=3,max_length=100)
    description:str=Field(...,min_length=5)
                        
