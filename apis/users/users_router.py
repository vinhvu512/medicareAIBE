from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.session import get_db
from apis.authenticate.authenticate import get_current_user
from models.user import User

router = APIRouter()

@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user information based on token"""
    try:
        return {
            "username": current_user.username,
            "email": current_user.email,
            "user_type": current_user.user_type,
            "fullname": current_user.fullname,
            "date_of_birth": str(current_user.date_of_birth),
            "gender": current_user.gender,
            "address": current_user.address or None,
            "phone": current_user.phone or None,
            "profile_image": current_user.profile_image or None
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Unable to retrieve current user",
                "code": 500
            }
        )