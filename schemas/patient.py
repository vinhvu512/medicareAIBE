from pydantic import BaseModel
from .user import User

class PatientBase(BaseModel):
    m_profile_image: str | None = None

class PatientCreate(PatientBase):
    pass

class Patient(PatientBase):
    m_patient_id: int
    user: User

    class Config:
        from_attributes = True