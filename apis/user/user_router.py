from fastapi import APIRouter, HTTPException
from models.user import User

router = APIRouter()

@router.get("/me")
async def get_current_user_info():
    """
    Get current user information without validating token.
    
    This assumes the user is already authenticated and their data is available.
    """
    try:
        # Dữ liệu giả lập user đã được xác thực (test purpose)
        current_user = User(
            m_username="john_doe",
            m_email="john@example.com",
            m_user_type="PATIENT",
            m_fullname="John Doe",
            m_date_of_birth="1990-01-01",
            m_gender="MALE",
            m_address="123 Main St",
            m_phone="123456789",
            m_profile_image="https://example.com/image.jpg"
        )

        # Trả về thông tin người dùng
        return {
            "code": 200,
            "message": "User retrieved successfully",
            "user_data": {
                "username": current_user.m_username,
                "email": current_user.m_email,
                "user_type": current_user.m_user_type,
                "fullname": current_user.m_fullname,
                "date_of_birth": str(current_user.m_date_of_birth),
                "gender": current_user.m_gender,
                "address": current_user.m_address or None,
                "phone": current_user.m_phone or None,
                "profile_image": current_user.m_profile_image or None
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": 500,
                "message": f"Unable to retrieve current user: {str(e)}"
            }
        )