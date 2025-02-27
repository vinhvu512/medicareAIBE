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
from schemas.user import UserSignUp

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/signup")
async def signup(user_data: UserSignUp, db: Session = Depends(get_db)):
    # Check unique username
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )
        
    # Check unique email
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )
    
    try:
        # Hash password
        hashed_password = pwd_context.hash(user_data.password)
        
        # Create base user
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            password=hashed_password,
            fullname=user_data.fullname,
            date_of_birth=user_data.date_of_birth,
            gender=user_data.gender,
            user_type=user_data.user_type,
            address=user_data.address,
            phone=user_data.phone,
            profile_image=user_data.profile_image
        )
        db.add(db_user)
        db.flush()

        # Create associated profile based on user type
        if user_data.user_type == UserTypeEnum.PATIENT:
            patient = Patient(
                patient_id=db_user.user_id
            )
            db.add(patient)
            
        elif user_data.user_type == UserTypeEnum.DOCTOR:
            if not user_data.doctor_specialty:
                raise ValueError("Doctor specialty is required for doctor users")
                
            doctor = Doctor(
                doctor_id=db_user.user_id,
                doctor_specialty=user_data.doctor_specialty,
                doctor_experience=user_data.doctor_experience
            )
            db.add(doctor)

        db.commit()
        db.refresh(db_user)
        
        return {
            "user_id": db_user.user_id,
            "username": db_user.username,
            "email": db_user.email,
            "user_type": db_user.user_type,
            "message": "User created successfully"
        }
        
    except ValueError as ve:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")