from pydantic import BaseModel, EmailStr

class HospitalBase(BaseModel):
    hospital_name: str
    hospital_address: str | None = None
    hospital_phone: str | None = None
    hospital_email: EmailStr | None = None
    hospital_image: str | None = None

class HospitalCreate(HospitalBase):
    pass

class Hospital(HospitalBase):
    hospital_id: int

    class Config:
        from_attributes = True