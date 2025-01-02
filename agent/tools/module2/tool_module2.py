import sys
import os
# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from datetime import date
from sqlalchemy.orm import Session
from database.session import SessionLocal
from models.user import User, GenderEnum, UserTypeEnum
from models.patient import Patient
from models.doctor import Doctor

def add_user(
    username: str,
    email: str,
    password: str,  # Added password parameter
    date_of_birth: date,
    gender: GenderEnum,
    user_type: UserTypeEnum,
    address: str = None,
    phone: str = None,
    profile_image: str = None,
    doctor_specialty: str = None,
    doctor_experience: int = None
) -> User:
    db = SessionLocal()
    try:
        # Create base user with password
        db_user = User(
            UserName=username,
            Email=email,
            Password=password,  # Added password
            DateOfBirth=date_of_birth,
            Gender=gender,
            UserType=user_type,
            Address=address,
            Phone=phone,
            ProfileImage=profile_image
        )
        db.add(db_user)
        db.flush()  # Get the user ID without committing
        
        # Create associated profile based on user type
        if user_type == UserTypeEnum.PATIENT:
            patient = Patient(
                PatientID=db_user.UserID,
                ProfileImage=profile_image
            )
            db.add(patient)
            
        elif user_type == UserTypeEnum.DOCTOR:
            if not doctor_specialty or doctor_experience is None:
                raise ValueError("Doctor specialty and experience are required for doctor users")
                
            doctor = Doctor(
                DoctorID=db_user.UserID,
                DoctorSpecialty=doctor_specialty,
                DoctorExperience=doctor_experience,
                ProfileImage=profile_image
            )
            db.add(doctor)
        
        db.commit()
        db.refresh(db_user)
        return db_user
        
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

# Example usage:
if __name__ == "__main__":
    # Example: Add a new patient
    try:
        new_patient = add_user(
            username="John Doe 1",
            password="4321",
            email="john.doe1@example.com",
            date_of_birth=date(1990, 1, 1),
            gender=GenderEnum.MALE,
            user_type=UserTypeEnum.PATIENT,
            address="123 Main St",
            phone="1234567890"
        )
        print(f"Created patient user: {new_patient.UserName}")
        
        # Example: Add a new doctor
        new_doctor = add_user(
            username="Dr. Jane Smith 1",
            email="jane.smith1@example.com",
            password="4321",
            date_of_birth=date(1985, 5, 15),
            gender=GenderEnum.FEMALE,
            user_type=UserTypeEnum.DOCTOR,
            address="456 Hospital Ave",
            phone="0987654321",
            doctor_specialty="Cardiology",
            doctor_experience=10
        )
        print(f"Created doctor user: {new_doctor.UserName}")
        
    except Exception as e:
        print(f"Error creating user: {str(e)}")