from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import Dict, List
from schemas.doctor import WeekDay
from database.session import get_db
from models.doctor import Doctor
from models.user import User
from schemas.doctor import Doctor as DoctorSchema
from models.relationships import DoctorHospital
from pydantic import BaseModel
from datetime import date

router = APIRouter()

class DoctorUserResponse(BaseModel):
    user_id: int
    username: str
    email: str
    user_type: str
    fullname: str
    date_of_birth: date
    gender: str
    address: str | None
    phone: str | None
    profile_image: str | None
    doctor_specialty: str
    doctor_experience: int | None

    class Config:
        from_attributes = True

@router.get("/search", response_model=List[DoctorUserResponse])
async def get_doctors_by_department(
    hospital_id: int = Query(..., description="Hospital ID"),
    department_id: int = Query(..., description="Department ID"),
    db: Session = Depends(get_db)
):
    """
    Get all doctors working in a specific department at a specific hospital.
    """
    try:
        doctors = db.query(Doctor)\
            .options(joinedload(Doctor.user))\
            .join(DoctorHospital, Doctor.doctor_id == DoctorHospital.doctor_id)\
            .filter(
                DoctorHospital.hospital_id == hospital_id,
                DoctorHospital.department_id == department_id,
                DoctorHospital.relationship_status == 'Active'
            )\
            .all()

        if not doctors:
            return {
                "code": 404,
                "message": f"No doctors found for hospital ID {hospital_id} and department ID {department_id}",
                "data": []
            }

        doctor_list = [
            {
                "user_id": doctor.user.user_id,
                "username": doctor.user.username,
                "email": doctor.user.email,
                "user_type": doctor.user.user_type,
                "fullname": doctor.user.fullname,
                "date_of_birth": doctor.user.date_of_birth,
                "gender": doctor.user.gender,
                "address": doctor.user.address,
                "phone": doctor.user.phone,
                "profile_image": doctor.user.profile_image,
                "doctor_specialty": doctor.doctor_specialty,
                "doctor_experience": doctor.doctor_experience
            }
            for doctor in doctors
        ]

        return {
            "code": 200,
            "message": "Doctors retrieved successfully",
            "data": doctor_list
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": 500,
                "message": f"Error fetching doctors: {str(e)}"
            }
        )

@router.put("/schedule/{doctor_id}")
async def update_doctor_schedule(
    doctor_id: int,
    weekly_schedule: Dict[str, List[int]],
    db: Session = Depends(get_db)
):
    """
    Update a doctor's weekly schedule.
    """
    try:
        doctor = db.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()
        if not doctor:
            return {
                "code": 404,
                "message": f"Doctor with ID {doctor_id} not found",
                "data": None
            }

        valid_days = [day.value for day in WeekDay]
        for day, shifts in weekly_schedule.items():
            if day not in valid_days:
                return {
                    "code": 400,
                    "message": f"Invalid day: {day}. Must be one of {valid_days}",
                    "data": None
                }
            if not all(0 <= shift <= 19 for shift in shifts):
                return {
                    "code": 400,
                    "message": "Shifts must be between 0 and 19",
                    "data": None
                }

        doctor.weekly_schedule = weekly_schedule
        db.commit()

        return {
            "code": 200,
            "message": "Schedule updated successfully",
            "data": {
                "doctor_id": doctor_id,
                "weekly_schedule": weekly_schedule
            }
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "code": 500,
                "message": f"Failed to update schedule: {str(e)}"
            }
        )