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
from datetime import datetime, date

from datetime import datetime, timedelta
from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.session import get_db
from models.doctor import Doctor
from models.appointment import Appointment, AppointmentStatusEnum
from schemas.doctor import WeekDay

from apis.authenticate.authenticate import get_current_patient  # Add this import
from models.user import User # Add this import
from models.doctor import Doctor

router = APIRouter()

@router.post("", response_model=AppointmentResponse)
async def create_appointment(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db)
    # current_user: User = Depends(get_current_patient)
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

        # # Validate department exists
        # department = db.query(Department).filter(
        #     Department.department_id == appointment.department_id,
        #     Department.hospital_id == appointment.hospital_id
        # ).first()
        # if not department:
        #     raise HTTPException(
        #         status_code=404,
        #         detail={
        #             "error": "Department not found in this hospital",
        #             "code": 404
        #         }
        #     )

        # # Validate room exists if provided
        # if appointment.room_id:
        #     room = db.query(ClinicRoom).filter(
        #         ClinicRoom.room_id == appointment.room_id,
        #         ClinicRoom.department_id == appointment.department_id,
        #         ClinicRoom.hospital_id == appointment.hospital_id
        #     ).first()
        #     if not room:
        #         raise HTTPException(
        #             status_code=404,
        #             detail={
        #                 "error": "Room not found in this department",
        #                 "code": 404
        #             }
        #         )

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
            Appointment.hospital_id == appointment.hospital_id,
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
            room_id=appointment.doctor_id-49,
            doctor_id=appointment.doctor_id,
            patient_id=appointment.patient_id,
            appointment_day=appointment.appointment_day,
            appointment_shift=appointment.appointment_shift,
            reason=appointment.reason,
            status=AppointmentStatusEnum.SCHEDULED
        )

        db.add(new_appointment)
        db.flush()
        db.commit()

        # Join với bảng User và Doctor để lấy thông tin bác sĩ
        doctor_info = db.query(User, Doctor)\
            .join(Doctor, User.user_id == Doctor.doctor_id)\
            .filter(User.user_id == appointment.doctor_id)\
            .first()

        # Tạo response với thông tin bổ sung về bác sĩ
        appointment_response = {
            "appointment_id": new_appointment.appointment_id,
            "hospital_id": new_appointment.hospital_id,
            "department_id": new_appointment.department_id,
            "doctor_id": new_appointment.doctor_id,
            "doctor_fullname": doctor_info[0].fullname,  # Lấy từ User model
            "doctor_specialty": doctor_info[1].doctor_specialty,  # Lấy từ Doctor model
            "patient_id": new_appointment.patient_id,
            "appointment_day": new_appointment.appointment_day,
            "appointment_shift": new_appointment.appointment_shift,
            "reason": new_appointment.reason,
            "status": new_appointment.status
        }

        print("Debug ", appointment_response)
        return appointment_response

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

@router.get("", response_model=List[AppointmentResponse])
async def get_user_appointments(
    user_id: int = Query(..., description="ID of the user to get appointments for"),
    status: AppointmentStatusEnum | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    db: Session = Depends(get_db)
):
    """Get all appointments for a specific user"""
    try:
        # Build query
        query = db.query(Appointment, User, Doctor)\
            .join(Doctor, Appointment.doctor_id == Doctor.doctor_id)\
            .join(User, Doctor.doctor_id == User.user_id)\
            .filter(Appointment.patient_id == user_id)
        
        if status:
            query = query.filter(Appointment.status == status)
        if start_date:
            query = query.filter(Appointment.appointment_day >= start_date)
        if end_date:
            query = query.filter(Appointment.appointment_day <= end_date)

        # Get results
        results = query.order_by(
            Appointment.appointment_day.asc(),
            Appointment.appointment_shift.asc()
        ).all()

        # Format response with doctor info
        appointments = []
        for appointment, user, doctor in results:
            appointment_data = {
                "appointment_id": appointment.appointment_id,
                "hospital_id": appointment.hospital_id,
                "department_id": appointment.department_id,
                "room_id": appointment.room_id,
                "doctor_id": appointment.doctor_id,
                "doctor_fullname": user.fullname,
                "doctor_specialty": doctor.doctor_specialty,
                "patient_id": appointment.patient_id,
                "appointment_day": appointment.appointment_day,
                "appointment_shift": appointment.appointment_shift,
                "reason": appointment.reason,
                "status": appointment.status
            }
            appointments.append(appointment_data)

        return appointments or []

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"Error fetching appointments: {str(e)}",
                "code": 500
            }
        )
    
@router.get("/available-appointments")
async def get_available_appointments(
    hospital_id: int,
    department_id: int,
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient)
):
    try:
        # Get doctor's info with User join
        doctor_info = db.query(Doctor, User)\
            .join(User, Doctor.doctor_id == User.user_id)\
            .filter(Doctor.doctor_id == doctor_id)\
            .first()
            
        if not doctor_info:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": f"Doctor with ID {doctor_id} not found",
                    "code": 404
                }
            )
            
        doctor, user = doctor_info

        # Get today's date
        today = datetime.now().date()
        start_date = today + timedelta(days=1)
        end_date = start_date + timedelta(days=7)

        print("start ", start_date, " end ", end_date)

        # Get doctor's weekly schedule
        weekly_schedule = doctor.weekly_schedule or {}

        # Get existing appointments for this doctor in the date range
        existing_appointments = db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.hospital_id == hospital_id,
            Appointment.department_id == department_id,
            Appointment.appointment_day >= start_date,
            Appointment.appointment_day <= end_date,
            Appointment.status.in_([AppointmentStatusEnum.SCHEDULED, AppointmentStatusEnum.IN_PROGRESS])
        ).all()

        # Create a set of booked slots (day and shift combinations)
        booked_slots = {
            (app.appointment_day, app.appointment_shift) 
            for app in existing_appointments
        }

        print("slot num ", len(booked_slots))

        # Generate available appointments excluding booked slots
        available_appointments = []
        current_date = start_date

        while current_date <= end_date:
            day_name = current_date.strftime("%A")
            day_shifts = weekly_schedule.get(day_name, [])
            
            for shift in day_shifts:
                # Only add slot if it's not already booked
                if (current_date, shift["shift_id"]) not in booked_slots:
                    available_appointments.append({
                        "appointment_day": current_date,
                        "appointment_shift": shift["shift_id"],
                        "room_id": shift["room_id"]
                    })
            
            current_date += timedelta(days=1)

        return {
            "hospital_id": hospital_id,
            "department_id": department_id,
            "doctor_id": doctor_id,
            "available_appointments": available_appointments
        }

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"Error fetching available appointments: {str(e)}",
                "code": 500
            }
        )
    

@router.get("/by-day-shift")
async def get_appointment_by_day_shift(
    appointment_day: str,  # Changed from date to str
    shift_id: int,
    db: Session = Depends(get_db)
):
    """
    Lấy thông tin cuộc hẹn dựa trên ngày và ca khám.
    
    Parameters:
        appointment_day: Ngày hẹn (format: YYYY-MM-DD)
        shift_id: ID ca khám
    """
    try:
        # Convert string to date object
        appointment_date = datetime.strptime(appointment_day, "%Y-%m-%d").date()
        
        # Query appointment với ngày và ca khám cụ thể
        appointment = db.query(Appointment).filter(
            Appointment.appointment_day == appointment_date,
            Appointment.appointment_shift == shift_id
        ).first()

        if not appointment:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Không tìm thấy cuộc hẹn với ngày và ca khám này",
                    "code": 404
                }
            )

        return {
            "appointment_id": appointment.appointment_id,
            "hospital_id": appointment.hospital_id,
            "department_id": appointment.department_id,
            "doctor_id": appointment.doctor_id,
            "patient_id": appointment.patient_id,
            "appointment_day": appointment.appointment_day,
            "appointment_shift": appointment.appointment_shift,
            "status": appointment.status
        }

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"Lỗi khi lấy thông tin cuộc hẹn: {str(e)}",
                "code": 500
            }
        )