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

@router.post("", response_model=ClinicRoomSchema)
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
                detail={
                    "error": f"Hospital with id {room_data.hospital_id} not found",
                    "code": 404
                }
            )

        # Verify department exists
        department = db.query(Department).filter(Department.department_id == room_data.department_id).first()
        if not department:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": f"Department with id {room_data.department_id} not found",
                    "code": 500
                }
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
            detail={
                "error": f"Failed to create clinic room: {str(e)}",
                "code": 500
            }
        )