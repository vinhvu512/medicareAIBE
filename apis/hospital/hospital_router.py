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


router = APIRouter()

@router.post("/hospitals", response_model=HospitalSchema)
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
    
@router.post("/departments", response_model=DepartmentSchema)
async def create_department(
    department_data: DepartmentCreate,
    db: Session = Depends(get_db)
):
    """Create a new department"""
    try:
        # Verify hospital exists
        hospital = db.query(Hospital).filter(Hospital.hospital_id == department_data.hospital_id).first()
        if not hospital:
            raise HTTPException(
                status_code=404,
                detail=f"Hospital with id {department_data.hospital_id} not found"
            )

        # Create new department
        new_department = Department(
            department_name=department_data.department_name,
            department_location=department_data.department_location,
            hospital_id=department_data.hospital_id
        )
        
        db.add(new_department)
        db.commit()
        db.refresh(new_department)
        
        return new_department
        
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create department: {str(e)}"
        )

@router.post("/clinic-rooms", response_model=ClinicRoomSchema)
async def create_clinic_room(
    room_data: ClinicRoomCreate,
    db: Session = Depends(get_db)
):
    """Create a new clinic room"""
    try:
        # Verify hospital exists
        hospital = db.query(Hospital).filter(Hospital.hospital_id == room_data.hospital_id).first()
        if not hospital:
            raise HTTPException(
                status_code=404,
                detail=f"Hospital with id {room_data.hospital_id} not found"
            )

        # Verify department exists
        department = db.query(Department).filter(Department.department_id == room_data.department_id).first()
        if not department:
            raise HTTPException(
                status_code=404,
                detail=f"Department with id {room_data.department_id} not found"
            )

        # Create new clinic room
        new_room = ClinicRoom(
            room_name=room_data.room_name,
            room_location=room_data.room_location,
            room_image=room_data.room_image,
            department_id=room_data.department_id,
            hospital_id=room_data.hospital_id
        )
        
        db.add(new_room)
        db.commit()
        db.refresh(new_room)
        
        return new_room
        
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create clinic room: {str(e)}"
        )

# Thêm endpoint mới vào router hiện có
@router.get("/search", response_model=List[HospitalSchema])
async def search_hospitals(
    query: str = Query(..., description="Search query for hospital name"),
    db: Session = Depends(get_db)
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
    
@router.get("/", response_model=List[HospitalSchema])
async def get_all_hospitals(
    db: Session = Depends(get_db),
    skip: int = Query(0, description="Skip x records"),
    limit: int = Query(100, description="Limit the number of records returned")
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