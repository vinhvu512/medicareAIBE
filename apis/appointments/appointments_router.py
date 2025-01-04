from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.session import get_db
from models.appointment import Appointment, AppointmentStatusEnum
from models.doctor import Doctor
from models.hospital import Hospital
from models.department import Department
from models.clinic_room import ClinicRoom
from models.patient import Patient
from schemas.appointment import AppointmentCreate, AppointmentResponse

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
            return {
                "code": 404,
                "message": "Hospital not found",
                "data": None
            }

        # Validate department exists
        department = db.query(Department).filter(
            Department.department_id == appointment.department_id,
            Department.hospital_id == appointment.hospital_id
        ).first()
        if not department:
            return {
                "code": 404,
                "message": "Department not found in this hospital",
                "data": None
            }

        # Validate room exists if provided
        if appointment.room_id:
            room = db.query(ClinicRoom).filter(
                ClinicRoom.room_id == appointment.room_id,
                ClinicRoom.department_id == appointment.department_id,
                ClinicRoom.hospital_id == appointment.hospital_id
            ).first()
            if not room:
                return {
                    "code": 404,
                    "message": "Room not found in this department",
                    "data": None
                }

        # Validate doctor exists
        doctor = db.query(Doctor).filter(
            Doctor.doctor_id == appointment.doctor_id
        ).first()
        if not doctor:
            return {
                "code": 404,
                "message": "Doctor not found",
                "data": None
            }

        # Validate patient exists
        patient = db.query(Patient).filter(
            Patient.patient_id == appointment.patient_id
        ).first()
        if not patient:
            return {
                "code": 404,
                "message": "Patient not found",
                "data": None
            }

        # Check if doctor is available at this time
        existing_appointment = db.query(Appointment).filter(
            Appointment.doctor_id == appointment.doctor_id,
            Appointment.appointment_day == appointment.appointment_day,
            Appointment.appointment_shift == appointment.appointment_shift,
            Appointment.status.in_([AppointmentStatusEnum.SCHEDULED, AppointmentStatusEnum.IN_PROGRESS])
        ).first()

        if existing_appointment:
            return {
                "code": 409,
                "message": "Doctor is not available at this time",
                "data": None
            }

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

        return {
            "code": 201,
            "message": "Appointment created successfully",
            "data": new_appointment
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "code": 500,
                "message": f"Failed to create appointment: {str(e)}"
            }
        )