from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database.session import get_db
from models.appointment import Appointment, AppointmentStatusEnum
from models.doctor import Doctor
from models.hospital import Hospital
from models.department import Department
from models.clinic_room import ClinicRoom
from models.patient import Patient
from schemas.appointment import AppointmentCreate, AppointmentResponse
from datetime import datetime

router = APIRouter()

@router.post("/appointments", response_model=AppointmentResponse)
async def create_appointment(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db)
):
    """Create a new appointment"""
    try:
        # Validate hospital exists
        hospital = db.query(Hospital).filter(
            Hospital.hospital_id == appointment.hospital_id
        ).first()
        if not hospital:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Hospital not found",
                    "code": 404
                }
            )

        # Validate department exists
        department = db.query(Department).filter(
            Department.department_id == appointment.department_id,
            Department.hospital_id == appointment.hospital_id
        ).first()
        if not department:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Department not found in this hospital",
                    "code": 404
                }
            )

        # Validate room exists if provided
        if appointment.room_id:
            room = db.query(ClinicRoom).filter(
                ClinicRoom.room_id == appointment.room_id,
                ClinicRoom.department_id == appointment.department_id,
                ClinicRoom.hospital_id == appointment.hospital_id
            ).first()
            if not room:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "Room not found in this department",
                        "code": 404
                    }
                )

        # Validate doctor exists
        doctor = db.query(Doctor).filter(
            Doctor.doctor_id == appointment.doctor_id
        ).first()
        if not doctor:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Doctor not found",
                    "code": 404
                }
            )

        # Validate patient exists
        patient = db.query(Patient).filter(
            Patient.patient_id == appointment.patient_id
        ).first()
        if not patient:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Patient not found",
                    "code": 404
                }
            )

        # Check if doctor is available at this time
        existing_appointment = db.query(Appointment).filter(
            Appointment.doctor_id == appointment.doctor_id,
            Appointment.appointment_day == appointment.appointment_day,
            Appointment.appointment_shift == appointment.appointment_shift,
            Appointment.status.in_([AppointmentStatusEnum.SCHEDULED, AppointmentStatusEnum.IN_PROGRESS])
        ).first()

        if existing_appointment:
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "Doctor is not available at this time",
                    "code": 409
                }
            )

        # Create new appointment
        new_appointment = Appointment(
            hospital_id=appointment.hospital_id,
            department_id=appointment.department_id,
            room_id=appointment.room_id,
            doctor_id=appointment.doctor_id,
            patient_id=appointment.patient_id,
            appointment_day=appointment.appointment_day,
            appointment_shift=appointment.appointment_shift,
            reason=appointment.reason,
            status=AppointmentStatusEnum.SCHEDULED
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