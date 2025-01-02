from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apis.register.register_router import router as register_router
from apis.login.login_router import router as login_router
from apis.test_token.test_token_router import router as test_token_router
from apis.user.user_router import router as user_router
from apis.hospital.hospital_router import router as hospital_router

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
app.include_router(register_router, prefix="/api/auth", tags=["registration"])
app.include_router(login_router, prefix="/api/auth", tags=["login"])
app.include_router(test_token_router, prefix="/api/auth", tags=["test_token"])
app.include_router(user_router, prefix="/api/auth", tags=["user"])
app.include_router(hospital_router, prefix="/api/hospital", tags=["hospitals"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)