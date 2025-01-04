from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import Dict, List
from schemas.doctor import WeekDay, ShiftSchedule
from database.session import get_db
from models.doctor import Doctor
from models.user import User
from schemas.doctor import Doctor as DoctorSchema
from models.relationships import DoctorHospital
from pydantic import BaseModel
from datetime import date

router = APIRouter()

# Create a new response model
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

@router.get("/{doctor_id}", response_model=DoctorUserResponse)
async def get_doctor_by_id(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    """
    Get doctor information by doctor_id.
    Returns doctor's details including user information.
    """
    try:
        doctor = db.query(Doctor)\
            .options(joinedload(Doctor.user))\
            .filter(Doctor.doctor_id == doctor_id)\
            .first()

        if not doctor:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": f"Doctor with ID {doctor_id} not found",
                    "code": 404
                }
            )

        # Transform the response to match DoctorUserResponse model
        doctor_data = {
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

        return doctor_data

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"Error fetching doctor: {str(e)}",
                "code": 500
            }
        )

@router.get("/search/{hospital_id}/{department_id}", response_model=List[DoctorUserResponse])
async def get_doctors_by_department(
    hospital_id: int,
    department_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all doctors working in a specific department at a specific hospital.
    Returns doctors based on hospital_id and department_id from doctor_hospitals relationship.
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
            raise HTTPException(
                status_code=404,
                detail={
                    "error": f"No doctors found for hospital ID {hospital_id} and department ID {department_id}",
                    "code": 404
                }
            )

        # Transform the response
        doctor_list = []
        for doctor in doctors:
            doctor_data = {
                # User fields
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
            doctor_list.append(doctor_data)

        return doctor_list

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"Error fetching doctors: {str(e)}",
                "code": 500
            }
        )
    
@router.put("/schedule/{doctor_id}", response_model=Dict)
async def update_doctor_schedule(
    doctor_id: int,
    weekly_schedule: Dict[str, List[ShiftSchedule]],  # Change the type annotation
    db: Session = Depends(get_db)
):
    """
    Update a doctor's weekly schedule
    - doctor_id: ID of the doctor
    - weekly_schedule: Dictionary with days as keys and list of ShiftSchedule objects as values
    """
    try:
        # Find the doctor
        doctor = db.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()
        if not doctor:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": f"Doctor with ID {doctor_id} not found",
                    "code": 404
                }
            )

        # Validate schedule format
        valid_days = [day.value for day in WeekDay]
        for day, shifts in weekly_schedule.items():
            if day not in valid_days:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": f"Invalid day: {day}. Must be one of {valid_days}",
                        "code": 400
                    }
                )
            for shift in shifts:
                if not (0 <= shift.shift_id <= 19):
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "error": "Shifts must be between 0 and 19",
                            "code": 400
                        }
                    )

        # Convert ShiftSchedule objects to dict before storing
        schedule_dict = {
            day: [{"shift_id": s.shift_id, "room_id": s.room_id} for s in shifts]
            for day, shifts in weekly_schedule.items()
        }

        # Update schedule
        doctor.weekly_schedule = schedule_dict
        db.commit()

        return {
            "message": "Schedule updated successfully",
            "doctor_id": doctor_id,
            "weekly_schedule": schedule_dict
        }

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"Failed to update schedule: {str(e)}",
                "code": 500
            }
        )