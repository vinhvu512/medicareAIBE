from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apis.signup.signup_router import router as signup_router
from apis.login.login_router import router as login_router
from apis.test_token.test_token_router import router as test_token_router
from apis.users.users_router import router as users_router
from apis.hospitals.hospitals_router import router as hospitals_router
from apis.appointments.appointments_router import router as appointments_router
from apis.relationships.relationships_router import router as relationships_router
from apis.doctors.doctors_router import router as doctors_router
from apis.departments.departments_router import router as departments_router
from apis.clinic_rooms.clinic_rooms_router import router as clinic_rooms_router
from apis.mapbox.mapbox_router import router as mapbox_router

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.session import get_db
from apis.authenticate.authenticate import get_current_user
from models.user import User

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(signup_router, prefix="/api/auth", tags=["signup"])
app.include_router(login_router, prefix="/api/auth", tags=["login"])
app.include_router(test_token_router, prefix="/api/auth", tags=["test_token"])
app.include_router(users_router, prefix="/api/auth", tags=["user"])
app.include_router(hospitals_router, prefix="/api/hospitals", tags=["hospitals"])
app.include_router(appointments_router, prefix="/api/appointments", tags=["appointments"])
app.include_router(relationships_router, prefix="/api/relationships", tags=["relationships"])
app.include_router(doctors_router, prefix="/api/doctors", tags=["doctors"])
app.include_router(departments_router, prefix="/api/departments", tags=["departments"])
app.include_router(clinic_rooms_router, prefix="/api/clinic-rooms", tags=["clinic_roooms"])
app.include_router(mapbox_router, prefix="/api/mapbox", tags=["mapbox"])

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=80, reload=True)