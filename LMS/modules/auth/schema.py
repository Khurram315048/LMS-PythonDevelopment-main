
from pydantic import BaseModel ,EmailStr,Field



class SignupUser(BaseModel):
    first_name:str=Field(...,min_length=2)
    last_name:str=Field(...,min_length=2)
    contact:int
    email:EmailStr
    password:str=Field(...,min_length=8)
    user_type:str=Field(...,pattern="^(student|teacher|admin)$")