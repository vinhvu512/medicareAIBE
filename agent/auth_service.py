from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, Request

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

fake_users_db = {
    "admin@example.com": {
        "name": "Admin",
        "hashed_password": pwd_context.hash("123456"),
    },
    "doctor@medicare.com": {
        "name": "Dr. Smith",
        "hashed_password": pwd_context.hash("doctor123"),
    },
    "patient@gmail.com": {
        "name": "John Doe",
        "hashed_password": pwd_context.hash("patient123"), 
    },
    "staff@hospital.com": {
        "name": "Mary Johnson",
        "hashed_password": pwd_context.hash("staff123"),
    },
    "testadmin@medicare.com": {
        "name": "Test Admin",
        "hashed_password": pwd_context.hash("test123"),
    }
}

# Xác thực người dùng
def authenticate_user(email: str, password: str):
    user = fake_users_db.get(email)
    if not user or not pwd_context.verify(password, user['hashed_password']):
        return None
    return user

# Tạo token JWT
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})  # Thêm exp (hết hạn)
    print("Debug token ", jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM))
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Xác thực token (hàm verify_token)
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # Trả về payload giải mã được
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Token không hợp lệ hoặc đã hết hạn."
        )
