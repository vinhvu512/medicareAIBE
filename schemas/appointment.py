from pydantic import BaseModel, conint, validator
from datetime import datetime
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
    appointment_day: datetime
    appointment_shift: int  # Between 0-19
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

    class Config:
        from_attributes = True