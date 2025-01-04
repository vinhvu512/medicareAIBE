from pydantic import BaseModel, conint, Field, validator
from typing import Dict, List
from enum import Enum
from .user import User

class WeekDay(str, Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday" 
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"

class ShiftSchedule(BaseModel):
    shift_id: int
    room_id: int

class DoctorBase(BaseModel):
    doctor_specialty: str
    doctor_experience: int | None = 0
    profile_image: str | None = None
    weekly_schedule: Dict[str, List[ShiftSchedule]] = Field(
        default_factory=lambda: {day: [] for day in WeekDay}
    )

    @validator('weekly_schedule')
    def validate_shifts(cls, v):
        for day, shifts in v.items():
            for shift in shifts:
                if not (0 <= shift.shift_id <= 19):
                    raise ValueError("Shift ID must be between 0 and 19")
        return v

class DoctorCreate(DoctorBase):
    pass

class Doctor(DoctorBase):
    doctor_id: int
    user: User

    class Config:
        from_attributes = True