from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from database.session import get_db
from models.relationships import DoctorHospital, RelationshipStatusEnum
from models.doctor import Doctor
from models.hospital import Hospital
from schemas.relationships import DoctorHospitalCreate, DoctorHospital as DoctorHospitalSchema
from models.department import Department
from schemas.department import Department as DepartmentSchema

from datetime import date

router = APIRouter()

@router.post("/doctor-hospital", response_model=DoctorHospitalSchema)
async def create_doctor_hospital_relationship(
    relationship_data: DoctorHospitalCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new doctor-hospital relationship
    """
    try:
        # Check if doctor exists
        doctor = db.query(Doctor).filter(Doctor.doctor_id == relationship_data.doctor_id).first()
        if not doctor:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": f"Doctor with ID {relationship_data.doctor_id} not found",
                    "code": 404
                }
            )

        # Check if hospital exists
        hospital = db.query(Hospital).filter(Hospital.hospital_id == relationship_data.hospital_id).first()
        if not hospital:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": f"Hospital with ID {relationship_data.hospital_id} not found",
                    "code": 404
                }
            )

        # Check if department exists and belongs to hospital
        department = db.query(Department).filter(
            Department.department_id == relationship_data.department_id,
            Department.hospital_id == relationship_data.hospital_id
        ).first()
        if not department:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": f"Department ID {relationship_data.department_id} does not belong to Hospital ID {relationship_data.hospital_id}",
                    "code": 404
                }
            )

        # Check if relationship already exists and is active
        existing_relationship = db.query(DoctorHospital).filter(
            and_(
                DoctorHospital.doctor_id == relationship_data.doctor_id,
                DoctorHospital.hospital_id == relationship_data.hospital_id,
                DoctorHospital.department_id == relationship_data.department_id,
                DoctorHospital.relationship_status == RelationshipStatusEnum.ACTIVE
            )
        ).first()

        if existing_relationship:
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "Doctor-Hospital-Department relationship already exists",
                    "code": 409
                }
            )

        # Create new relationship
        new_relationship = DoctorHospital(
            doctor_id=relationship_data.doctor_id,
            hospital_id=relationship_data.hospital_id,
            department_id=relationship_data.department_id,
            work_schedule=relationship_data.work_schedule,
            start_date=relationship_data.start_date or date.today(),
            end_date=relationship_data.end_date,
            relationship_status=relationship_data.relationship_status or RelationshipStatusEnum.ACTIVE
        )

        db.add(new_relationship)
        db.commit()
        db.refresh(new_relationship)

        return new_relationship

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"Failed to create doctor-hospital relationship: {str(e)}",
                "code": 500
            }
        )