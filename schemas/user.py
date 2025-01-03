from pydantic import BaseModel, EmailStr
from datetime import date
from enum import Enum
from typing import Optional

class GenderEnum(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"

class UserTypeEnum(str, Enum):
    DOCTOR = "Doctor"
    PATIENT = "Patient"

class UserBase(BaseModel):
    username: str
    email: EmailStr
    user_type: UserTypeEnum
    fullname: str
    date_of_birth: date
    gender: GenderEnum
    address: str | None = None
    phone: str | None = None
    profile_image: str | None = None

class UserCreate(UserBase):
    password: str = "1234"

class User(UserBase):
    user_id: int
    
    class Config:
        from_attributes = True

class UserSignUp(UserCreate):
    doctor_specialty: Optional[str] = None
    doctor_experience: Optional[int] = None