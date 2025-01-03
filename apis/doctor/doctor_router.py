from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List
from database.session import get_db
from models.doctor import Doctor
from models.user import User
from schemas.doctor import Doctor as DoctorSchema
from models.relationships import DoctorHospital

router = APIRouter()

@router.get("/by-department", response_model=List[DoctorSchema])
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

        return doctors

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