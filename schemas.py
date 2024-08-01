from pydantic import BaseModel, EmailStr, field_validator 
import re

class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[0,1,2,3,4,5,6,7,8,9]', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

class User(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True


class UploadedFile(BaseModel):
    filename: str
    path : str 

    class Config:
        orm_mode = True

################

class JobDescription(BaseModel):
    description: str

    class Config:
        orm_mode = True

class Skills(BaseModel):
    skills: str

    class Config:
        orm_mode = True

class UploadFileResponse(BaseModel):
    filename: str
    content_type: str

    class Config:
        orm_mode = True



