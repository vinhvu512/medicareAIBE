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

# Cấu hình templates
templates = Jinja2Templates(directory="templates")

# Cấu hình JWT
SECRET_KEY = "your-secret-key"  # Thay bằng secret key thực tế
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Định nghĩa OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Giả lập cơ sở dữ liệu lưu trữ agent cho từng user và agent_id
import threading

# Giả lập cơ sở dữ liệu lưu trữ agent cho từng user và agent_id
user_agents: Dict[str, Dict[int, AgentService]] = {}
user_agents_lock = threading.Lock()

# Model cho request chat
class ChatRequest(BaseModel):
    query: str

# Model cho request đặt base prompt
class BasePromptRequest(BaseModel):
    prompt: str

# Hàm tạo access token
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Hàm lấy current user từ token
# main.py

def get_current_user(request: Request):
    token = request.cookies.get("Authorization") or request.headers.get("Authorization")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No token provided"
        )

    # Remove "Bearer " prefix if present
    token = token.replace("Bearer ", "") if token.startswith("Bearer ") else token
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        logging.info(f"Authenticated user_id: {user_id}")
        return {"user_id": user_id, "token": token}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )








def get_or_create_agent(user_id: str, agent_id: int) -> AgentService:
    with user_agents_lock:
        if user_id not in user_agents:
            user_agents[user_id] = {}
            logging.info(f"Initialized agent dictionary for user: {user_id}")
        if agent_id not in user_agents[user_id]:
            user_agents[user_id][agent_id] = AgentService()
            logging.info(f"New agent {agent_id} created for user: {user_id}")
            logging.debug(f"Current user_agents: {user_agents}")
        else:
            logging.info(f"Agent {agent_id} retrieved for user: {user_id}")
    return user_agents[user_id][agent_id]




# Đăng nhập API
@app.post("/login")
async def login_api(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Sử dụng email (form_data.username) làm 'sub' để đảm bảo định danh duy nhất
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}



# Giao diện đăng nhập
@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Xử lý đăng nhập form
@app.post("/web-login")
async def web_login(username: str = Form(...), password: str = Form(...)):
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    
    access_token = create_access_token(data={"sub": username})
    
    response = RedirectResponse(url="/chat", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="Authorization",
        value=f"Bearer {access_token}",
        httponly=False,  # Đặt thành False để JS có thể truy cập; True trong sản xuất nếu không cần
        max_age=1800,     # 30 phút
        secure=False,     # Đặt thành True trong sản xuất với HTTPS
        samesite="lax"
    )
    return response

# Đặt base prompt cho agent theo user và agent_id
# main.py

@app.put("/agent/{agent_id}/base-prompt")
async def set_base_prompt(
    agent_id: int,
    request: BasePromptRequest,
    current_user: Dict[str, str] = Depends(get_current_user)
):
    try:
        if not request.prompt or len(request.prompt.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Base prompt cannot be empty", "code": 400}
            )

        # Tạo cấu trúc base prompt nâng cao
        base_prompt = f"""You are an AI medical assistant named Medicare AI.

User Information:
{request.prompt}

Core Rules:
1. ALWAYS remember and use the user information provided above
2. When asked about user information, answer based on the context
3. Match response language to user's query language
4. For medical queries, provide only general information
5. Refer to healthcare professionals for specific medical advice
6. If information is not in context, say "Tôi không có thông tin về điều đó"
"""

        # Kiểm tra agent_id hợp lệ
        if agent_id not in [1, 2, 3]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Invalid agent ID", "code": 400}
            )

        # Lấy hoặc tạo agent cho user và agent_id
        agent = get_or_create_agent(current_user["user_id"], agent_id)

        # Trích xuất token từ current_user
        token = current_user.get("token")
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is missing."
            )

        # Đặt base prompt cho agent với token
        agent.set_base_prompt(base_prompt, token)
        return {"message": f"Base prompt updated for agent {agent_id}", "status": "success"}

    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(f"Error setting base prompt: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": str(e), "code": 500}
        )



# Lấy base prompt hiện tại cho agent của user
@app.get("/agent/{agent_id}/base-prompt")
async def get_base_prompt(
    agent_id: int,
    current_user: str = Depends(get_current_user)
):
    # Kiểm tra agent_id hợp lệ
    if agent_id not in [1, 2, 3]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Invalid agent ID", "code": 400}
        )
    
    agent = get_or_create_agent(current_user, agent_id)
    return {"base_prompt": agent.base_prompt}

# Trang chat
@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request, current_user: str = Depends(get_current_user)):
    return templates.TemplateResponse("chat.html", {"request": request, "user": current_user})

# API chat agent

@app.post("/chat/agent/{agent_id}")
async def chat_agent(
    agent_id: int,
    request: ChatRequest,
    current_user: Dict[str, str] = Depends(get_current_user)
):
    # Kiểm tra agent_id hợp lệ
    if agent_id not in [1, 2, 3]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent không tồn tại."
        )
    
    agent = get_or_create_agent(current_user["user_id"], agent_id)
    try:
        response = agent.chat(request.query, token=current_user["token"])
        return JSONResponse(content={"response": response})
    except Exception as e:
        logging.error(f"Chat error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing the chat request."
        )


# Đăng xuất
@app.get("/logout")
async def logout(current_user: str = Depends(get_current_user)):
    response = RedirectResponse(url="/")
    response.delete_cookie("Authorization")
    # Xóa các agent của người dùng khỏi user_agents
    if current_user in user_agents:
        del user_agents[current_user]
        logging.info(f"All agents for user {current_user} have been deleted.")
    return response

# Chạy ứng dụng
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
