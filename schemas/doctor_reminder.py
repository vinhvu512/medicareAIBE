from pydantic import BaseModel
from datetime import datetime


class DoctorReminderBase(BaseModel):
    appointment_id: int
    doctor_id: int
    patient_id: int
    reminder_content: str
    reminder_date: datetime


class DoctorReminderCreate(DoctorReminderBase):
    pass


class DoctorReminderResponse(DoctorReminderBase):
    reminder_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True