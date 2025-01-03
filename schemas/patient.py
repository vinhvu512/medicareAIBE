from pydantic import BaseModel
from .user import User

class PatientBase(BaseModel):
    profile_image: str | None = None

class PatientCreate(PatientBase):
    pass

class Patient(PatientBase):
    patient_id: int
    user: User

    class Config:
        from_attributes = True