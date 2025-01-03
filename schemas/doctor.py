from pydantic import BaseModel, conint
from .user import User

class DoctorBase(BaseModel):
    doctor_specialty: str
    doctor_experience: conint(ge=0)
    profile_image: str | None = None

class DoctorCreate(DoctorBase):
    pass

class Doctor(DoctorBase):
    doctor_id: int
    user: User

    class Config:
        from_attributes = True