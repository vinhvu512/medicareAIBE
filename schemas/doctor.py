from pydantic import BaseModel, conint
from .user import User

class DoctorBase(BaseModel):
    m_doctor_specialty: str
    m_doctor_experience: conint(ge=0)
    m_profile_image: str | None = None

class DoctorCreate(DoctorBase):
    pass

class Doctor(DoctorBase):
    m_doctor_id: int
    user: User

    class Config:
        from_attributes = True