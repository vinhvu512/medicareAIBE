# main.py

from fastapi import FastAPI, Depends, Request, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from jose import jwt, JWTError
from typing import Dict
import logging
import uvicorn
from datetime import datetime, timedelta

# Import các router
from apis.signup.signup_router import router as signup_router
from apis.login.login_router import router as login_router
from apis.test_token.test_token_router import router as test_token_router
from apis.user.user_router import router as user_router
from apis.hospital.hospital_router import router as hospital_router
from apis.appointments.appointments_router import router as appointments_router
from apis.relationships.relationships_router import router as relationships_router
from apis.doctor.doctor_router import router as doctor_router
from apis.department.department_router import router as department_router

# Import các dịch vụ
from agent.agent_service import AgentService
from agent.auth_service import authenticate_user, create_access_token, verify_token
from database.session import get_db
from models.user import User

# Cấu hình logging
logging.basicConfig(level=logging.INFO)

# Cấu hình ứng dụng FastAPI
app = FastAPI()

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Bạn có thể thay đổi thành các origin cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Bao gồm các router
app.include_router(signup_router, prefix="/api/auth", tags=["signup"])
app.include_router(login_router, prefix="/api/auth", tags=["login"])
app.include_router(test_token_router, prefix="/api/auth", tags=["test_token"])
app.include_router(user_router, prefix="/api/auth", tags=["user"])
app.include_router(hospital_router, prefix="/api/hospital", tags=["hospitals"])
app.include_router(appointments_router, prefix="/api", tags=["appointments"])
app.include_router(relationships_router, prefix="/api/relationships", tags=["relationships"])
app.include_router(doctor_router, prefix="/api/doctor", tags=["doctors"])
app.include_router(department_router, prefix="/api/department", tags=["departments"])


# Chạy ứng dụng
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)
