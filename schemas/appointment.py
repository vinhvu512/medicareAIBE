from pydantic import BaseModel, conint, validator
from datetime import date
from enum import Enum

class AppointmentStatusEnum(str, Enum):
    SCHEDULED = "Scheduled"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"
    IN_PROGRESS = "InProgress"

class AppointmentBase(BaseModel):
    hospital_id: int
    department_id: int  
    room_id: int | None = None
    doctor_id: int
    patient_id: int
    appointment_day: date
    appointment_shift: int
    reason: str | None = None
    status: AppointmentStatusEnum = AppointmentStatusEnum.SCHEDULED

    @validator('appointment_shift')
    def validate_shift(cls, v):
        if not 0 <= v <= 19:
            raise ValueError('Shift must be between 0 and 19')
        return v

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentResponse(AppointmentBase):
    appointment_id: int
    doctor_fullname: str
    doctor_specialty: str

    class Config:
        from_attributes = True