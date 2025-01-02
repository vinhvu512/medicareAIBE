from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from datetime import date
from passlib.context import CryptContext
from models.user import User, GenderEnum, UserTypeEnum
from models.patient import Patient 
from models.doctor import Doctor
from database.session import get_db
from sqlalchemy.orm import Session
from typing import Optional

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    fullname: str
    date_of_birth: date
    gender: GenderEnum
    user_type: UserTypeEnum
    address: Optional[str] = None
    phone: Optional[str] = None
    profile_image: Optional[str] = None
    doctor_specialty: Optional[str] = None 
    doctor_experience: Optional[int] = None

@router.post("/register")
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    # Check unique username
    if db.query(User).filter(User.m_username == user_data.username).first():
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )
        
    # Check unique email
    if db.query(User).filter(User.m_email == user_data.email).first():
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )
    
    try:
        # Hash password
        hashed_password = pwd_context.hash(user_data.password)
        
        # Create base user
        db_user = User(
            m_username=user_data.username,
            m_email=user_data.email,
            m_password=hashed_password,
            m_fullname=user_data.fullname,
            m_date_of_birth=user_data.date_of_birth,
            m_gender=user_data.gender,
            m_user_type=user_data.user_type,
            m_address=user_data.address,
            m_phone=user_data.phone,
            m_profile_image=user_data.profile_image
        )
        db.add(db_user)
        db.flush()

        # Create associated profile based on user type
        if user_data.user_type == UserTypeEnum.PATIENT:
            patient = Patient(
                m_patient_id=db_user.m_user_id
            )
            db.add(patient)
            
        elif user_data.user_type == UserTypeEnum.DOCTOR:
            if not user_data.doctor_specialty:
                raise ValueError("Doctor specialty is required for doctor users")
                
            doctor = Doctor(
                m_doctor_id=db_user.m_user_id,
                m_doctor_specialty=user_data.doctor_specialty,
                m_doctor_experience=user_data.doctor_experience
            )
            db.add(doctor)

        db.commit()
        db.refresh(db_user)
        
        return {
            "status": "success",
            "message": "User registered successfully",
            "user_id": db_user.m_user_id
        }
        
    except ValueError as ve:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")