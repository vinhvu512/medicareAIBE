from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class AppointmentStatusEnum(str, Enum):
    SCHEDULED = "Scheduled"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"
    IN_PROGRESS = "InProgress"

class AppointmentBase(BaseModel):
    m_appointment_day: datetime
    m_appointment_status: AppointmentStatusEnum
    m_appointment_reason: str | None = None
    m_patient_id: int
    m_doctor_id: int
    m_room_id: int
    m_hospital_id: int

class AppointmentCreate(AppointmentBase):
    pass

class Appointment(AppointmentBase):
    m_appointment_id: int

    class Config:
        from_attributes = True