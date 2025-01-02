from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.session import get_db
from models.hospital import Hospital
from schemas.hospital import HospitalCreate, Hospital as HospitalSchema

router = APIRouter()

@router.post("/create_hospital", response_model=HospitalSchema)
async def create_hospital(
    hospital_data: HospitalCreate,
    db: Session = Depends(get_db)
):
    """Create a new hospital"""
    try:
        # Create new hospital instance
        new_hospital = Hospital(
            m_hospital_name=hospital_data.m_hospital_name,
            m_hospital_address=hospital_data.m_hospital_address,
            m_hospital_phone=hospital_data.m_hospital_phone,
            m_hospital_email=hospital_data.m_hospital_email,
            m_hospital_image=hospital_data.m_hospital_image
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