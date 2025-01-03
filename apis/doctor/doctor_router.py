from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List
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

@router.get("/search", response_model=List[DoctorUserResponse])
async def get_doctors_by_department(
    hospital_id: int = Query(..., description="Hospital ID"),
    department_id: int = Query(..., description="Department ID"),
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