from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
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