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
    user = authenticate_user(credentials.email, credentials.password, db)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={
            "sub": str(user.user_id),
            "user_type": user.user_type.value
        },
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    print("Token login ", type(user.user_type.value), " ", user.user_type.value)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.user_id,
        "user_type": user.user_type.value,
        "email": user.email,
        "fullname": user.fullname
    }