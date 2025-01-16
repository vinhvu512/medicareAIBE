from fastapi import APIRouter, Depends, HTTPException, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import List
from database.session import get_db
from models.hospital import Hospital
from schemas.hospital import HospitalCreate, Hospital as HospitalSchema
from models.department import Department
from models.clinic_room import ClinicRoom
from schemas.department import DepartmentCreate, Department as DepartmentSchema
from schemas.clinic_room import ClinicRoomCreate, ClinicRoom as ClinicRoomSchema

from apis.authenticate.authenticate import get_current_patient
from models.user import User

router = APIRouter()

@router.post("", response_model=HospitalSchema)
async def create_hospital(
    hospital_data: HospitalCreate,
    db: Session = Depends(get_db)
):
    """Create a new hospital"""
    try:
        # Create new hospital instance
        new_hospital = Hospital(
            hospital_name=hospital_data.hospital_name,
            hospital_address=hospital_data.hospital_address,
            hospital_phone=hospital_data.hospital_phone,
            hospital_email=hospital_data.hospital_email,
            hospital_image=hospital_data.hospital_image
        )
        
        # Add to database
        db.add(new_hospital)
        db.commit()
        db.refresh(new_hospital)
        
        return new_hospital
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create hospital: {str(e)}"
        )
    
@router.get("", response_model=List[HospitalSchema])
async def get_all_hospitals(
    db: Session = Depends(get_db),
    skip: int = Query(0, description="Skip x records"),
    limit: int = Query(100, description="Limit the number of records returned"),
    current_user: User = Depends(get_current_patient)
):
    """
    Get all hospitals with pagination support.
    Returns a list of all hospitals in the database.
    """
    try:
        hospitals = db.query(Hospital)\
            .offset(skip)\
            .limit(limit)\
            .all()

        if not hospitals:
            return []

        return hospitals

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"Error fetching hospitals: {str(e)}",
                "code": 500
            }
        )

@router.get("/search", response_model=List[HospitalSchema])
async def search_hospitals(
    query: str = Query(..., description="Search query for hospital name"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient)
):
    """
    Search hospitals using trigram similarity.
    Returns hospitals where name matches the search query above the given similarity threshold.
    """
    try:
        
        # Search using trigram similarity
        results = db.query(Hospital)\
            .filter(
                func.similarity(Hospital.hospital_name, query) > 0
            )\
            .order_by(
                func.similarity(Hospital.hospital_name, query).desc()
            )\
            .all()

        if not results:
            return []

        return results

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching hospitals: {str(e)}"
        )
    
@router.get("/{hospital_id}", response_model=HospitalSchema)
async def get_hospital_by_id(
    hospital_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient)
):
    """
    Get hospital information by hospital_id.
    Returns hospital's details.
    """
    try:
        hospital = db.query(Hospital)\
            .filter(Hospital.hospital_id == hospital_id)\
            .first()

        if not hospital:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": f"Hospital with ID {hospital_id} not found",
                    "code": 404
                }
            )

        return hospital

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"Error fetching hospital: {str(e)}",
                "code": 500
            }
        )