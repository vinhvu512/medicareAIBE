from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class AppointmentStatusEnum(str, Enum):
    SCHEDULED = "Scheduled"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"
    IN_PROGRESS = "InProgress"

class AppointmentBase(BaseModel):
    appointment_day: datetime
    appointment_status: AppointmentStatusEnum
    appointment_reason: str | None = None
    patient_id: int
    doctor_id: int
    room_id: int
    hospital_id: int

class AppointmentCreate(AppointmentBase):
    pass

class Appointment(AppointmentBase):
    appointment_id: int

    class Config:
        from_attributes = True