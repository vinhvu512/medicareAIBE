from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from database.session import get_db
from apis.authenticate.authenticate import authenticate_user, create_access_token
from datetime import timedelta

router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = 30

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/login")
async def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and generate an access token.
    
    Args:
        credentials (LoginRequest): User login credentials (email and password).
        db (Session): Database session.
        
    Returns:
        JSON response with access token and user details if credentials are valid.
    """
    # Xác thực người dùng
    user = authenticate_user(credentials.email, credentials.password, db)
    if not user:
        raise HTTPException(
            status_code=401,
            detail={
                "code": 401,
                "message": "Incorrect email or password"
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Tạo access token
    access_token = create_access_token(
        data={"sub": user.email},  # Sử dụng email thay vì username
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    # Trả về kết quả
    return {
        "code": 200,
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user_data": {
            "user_id": user.user_id,
            "user_type": user.user_type,
            "email": user.email,
            "fullname": user.fullname
        }
    }