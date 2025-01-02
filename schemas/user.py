from pydantic import BaseModel, EmailStr
from datetime import date
from enum import Enum

class GenderEnum(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"

class UserTypeEnum(str, Enum):
    DOCTOR = "Doctor"
    PATIENT = "Patient"

class UserBase(BaseModel):
    m_username: str
    m_email: EmailStr
    m_user_type: UserTypeEnum
    m_fullname: str
    m_date_of_birth: date
    m_gender: GenderEnum
    m_address: str | None = None
    m_phone: str | None = None
    m_profile_image: str | None = None

class UserCreate(UserBase):
    m_password: str = "1234"

class User(UserBase):
    m_user_id: int
    
    class Config:
        from_attributes = True