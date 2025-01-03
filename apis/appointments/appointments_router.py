from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from database.session import get_db
from models.appointment import Appointment, AppointmentStatusEnum
from models.doctor import Doctor
from models.patient import Patient
from models.clinic_room import ClinicRoom
from models.hospital import Hospital
from datetime import datetime
from pydantic import BaseModel

router = APIRouter()

class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    hospital_id: int
    room_id: int
    appointment_day: datetime
    appointment_reason: str

class AppointmentResponse(BaseModel):
    appointment_id: int
    patient_id: int
    doctor_id: int
    hospital_id: int
    room_id: int
    appointment_day: datetime
    appointment_reason: str
    appointment_status: AppointmentStatusEnum

    class Config:
        from_attributes = True

@router.post("/appointments", response_model=AppointmentResponse, status_code=201)
async def create_appointment(
    appointment_data: AppointmentCreate,
    db: Session = Depends(get_db)
):
    """Create a new appointment"""
    try:
        # Validate required fields
        if not all([
            appointment_data.patient_id,
            appointment_data.doctor_id,
            appointment_data.hospital_id,
            appointment_data.room_id,
            appointment_data.appointment_day
        ]):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Missing required fields",
                    "code": 400
                }
            )

        # Check if patient exists
        patient = db.query(Patient).filter(
            Patient.patient_id == appointment_data.patient_id
        ).first()
        if not patient:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Patient not found",
                    "code": 400
                }
            )

        # Check if doctor exists
        doctor = db.query(Doctor).filter(
            Doctor.doctor_id == appointment_data.doctor_id
        ).first()
        if not doctor:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Doctor not found",
                    "code": 400
                }
            )

        # Check if room exists
        room = db.query(ClinicRoom).filter(
            ClinicRoom.room_id == appointment_data.room_id
        ).first()
        if not room:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Room not found",
                    "code": 400
                }
            )

        # Check for scheduling conflicts
        existing_appointment = db.query(Appointment).filter(
            and_(
                Appointment.doctor_id == appointment_data.doctor_id,
                Appointment.appointment_day == appointment_data.appointment_day,
                Appointment.appointment_status.in_([
                    AppointmentStatusEnum.SCHEDULED,
                    AppointmentStatusEnum.IN_PROGRESS
                ])
            )
        ).first()

        if existing_appointment:
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "Appointment slot not available",
                    "code": 409
                }
            )

        # Create new appointment
        new_appointment = Appointment(
            patient_id=appointment_data.patient_id,
            doctor_id=appointment_data.doctor_id,
            hospital_id=appointment_data.hospital_id,
            room_id=appointment_data.room_id,
            appointment_day=appointment_data.appointment_day,
            appointment_reason=appointment_data.appointment_reason,
            appointment_status=AppointmentStatusEnum.SCHEDULED
        )

        db.add(new_appointment)
        db.commit()
        db.refresh(new_appointment)

        return new_appointment

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"Failed to create appointment: {str(e)}",
                "code": 500
            }
        )