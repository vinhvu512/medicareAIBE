from pydantic import BaseModel, EmailStr

class HospitalBase(BaseModel):
    m_hospital_name: str
    m_hospital_address: str | None = None
    m_hospital_phone: str | None = None
    m_hospital_email: EmailStr | None = None
    m_hospital_image: str | None = None

class HospitalCreate(HospitalBase):
    pass

class Hospital(HospitalBase):
    m_hospital_id: int

    class Config:
        from_attributes = True