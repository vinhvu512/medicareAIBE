from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database.session import get_db
from models.user import User, UserTypeEnum

# Constants
SECRET_KEY = "9c91618beb0577af1dc557ec13114119e108969f6856d671f6c964be44c09397"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def authenticate_user(email: str, password: str, db: Session) -> User | None:
    """Authenticate a user by email and password"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create JWT access token with user_id and user_type"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Get current authenticated user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials", 
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:

        
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        user_id: int = payload.get("sub")
        user_type: str = payload.get("user_type")
        
        if user_id is None or user_type is None:
            raise credentials_exception
        
        print("Here ", user_type, " ", type(user_type))
            
        # Get user from database by user_id
        user = db.query(User).filter(User.user_id == user_id).first()

        if user:
            print("get ok -", user.user_type.value, "- ", type(user.user_type.value), " -", user_type, "- ", type(user_type))

        if user is None or user.user_type.value != user_type:
            print("not ok")
            raise credentials_exception
        
        
        return user
        
    except JWTError:
        raise credentials_exception

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Verify user is active"""
    if not current_user:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_doctor(current_user: User = Depends(get_current_user)):
    if current_user.user_type != UserTypeEnum.DOCTOR:
        raise HTTPException(
            status_code=403,
            detail="Access forbidden. Doctor rights required."
        )
    return current_user

async def get_current_patient(current_user: User = Depends(get_current_user)):
    if current_user.user_type != UserTypeEnum.PATIENT:
        raise HTTPException(
            status_code=403,
            detail="Access forbidden. Patient rights required."
        )
    return current_user