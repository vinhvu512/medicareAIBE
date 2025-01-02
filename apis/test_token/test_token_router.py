from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.session import get_db
from apis.authenticate.authenticate import get_current_user
from models.user import User

router = APIRouter()

@router.get("/test-token")
async def test_token(current_user: User = Depends(get_current_user)):
    """Test endpoint to verify token validity"""
    return {
        "message": "Token is valid",
        "user_data": {
            "user_id": current_user.m_user_id,
            "email": current_user.m_email,
            "username": current_user.m_username,
            "user_type": current_user.m_user_type,
            "fullname": current_user.m_fullname
        }
    }