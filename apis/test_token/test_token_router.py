from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.session import get_db
from apis.authenticate.authenticate import get_current_user
from models.user import User

router = APIRouter()

@router.get("/test-token")
async def test_token(current_user: User = Depends(get_current_user)):
    """
    Test endpoint to verify token validity.

    Returns:
        A message confirming token validity along with user data.
    """
    try:
        # Kiểm tra nếu không có user (token không hợp lệ hoặc thiếu)
        if not current_user:
            raise HTTPException(
                status_code=401,
                detail={
                    "code": 401,
                    "message": "Invalid or missing token"
                }
            )

        # Trả về thông tin người dùng nếu token hợp lệ
        return {
            "code": 200,
            "message": "Token is valid",
            "user_data": {
                "user_id": current_user.user_id,
                "email": current_user.email,
                "username": current_user.username,
                "user_type": current_user.user_type,
                "fullname": current_user.fullname
            }
        }
    except HTTPException as http_error:
        # Xử lý các lỗi HTTPException (thường là 401)
        raise http_error
    except Exception as e:
        # Xử lý lỗi không mong muốn
        raise HTTPException(
            status_code=500,
            detail={
                "code": 500,
                "message": f"An unexpected error occurred: {str(e)}"
            }
        )