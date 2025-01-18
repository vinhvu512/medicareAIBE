
from fastapi import FastAPI, WebSocket, Depends, HTTPException, status, Request, Form
from fastapi.security import OAuth2PasswordBearer 
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Dict, List
import logging
import json
from datetime import datetime
import asyncio

from geminiagent.agent_service import AgentService
from traffic_service import check_traffic

# Import các dịch vụ

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from apis.authenticate.authenticate import get_current_user
from models.user import User


# Cấu hình logging
logging.basicConfig(level=logging.INFO)

# Cấu hình ứng dụng FastAPI
app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:80/api/auth/login")

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Bạn có thể thay đổi thành các origin cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cấu hình templates
templates = Jinja2Templates(directory="templates")

# Giả lập cơ sở dữ liệu lưu trữ agent cho từng user và agent_id
import threading



# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[str, WebSocket] = {}
        
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.user_connections[user_id] = websocket
        print(f"Client {user_id} connected")

    def disconnect(self, websocket: WebSocket, user_id: str):
        self.active_connections.remove(websocket)
        if user_id in self.user_connections:
            del self.user_connections[user_id]
        print(f"Client {user_id} disconnected")

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.user_connections:
            websocket = self.user_connections[user_id]
            await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()



# Giả lập cơ sở dữ liệu lưu trữ agent cho từng user và agent_id
user_agents: Dict[str, Dict[int, AgentService]] = {}
user_agents_lock = threading.Lock()


# Model cho request chat
class ChatRequest(BaseModel):
    query: str


# Model cho request đặt base prompt
class BasePromptRequest(BaseModel):
    prompt: str


async def get_or_create_agent(user_id: str, agent_id: int) -> AgentService:
    print("break 2.1")
    with user_agents_lock:
        if user_id not in user_agents:
            user_agents[user_id] = {}
            logging.info(f"Initialized agent dictionary for user: {user_id}")
        if agent_id not in user_agents[user_id]:
            user_agents[user_id][agent_id] = AgentService(agent_id=agent_id, user_id=user_id)
            logging.info(f"New agent {agent_id} created for user: {user_id}")
            logging.debug(f"Current user_agents: {user_agents}")
        else:
            logging.info(f"Agent {agent_id} retrieved for user: {user_id}")
    return user_agents[user_id][agent_id]

# WebSocket endpoint for Agent 1
@app.websocket("/ws/agent1/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        agent = await get_or_create_agent(user_id, 1)
        
        while True:
            data = await websocket.receive_text()
            try:
                print("Data ", data)
                message = json.loads(data)
                event = message.get('event', '')
                
                # if query:
                #     # Use the agent to process the query
                #     response = await agent.chat(query, None)  # You might need to handle token differently
                #     await manager.send_personal_message(str(response), user_id)

                if event == 'check location':
                    current_lat = float(message.get('current_lat', 0))
                    current_lon = float(message.get('current_lon', 0))

                    print(current_lon, current_lat)
                    
                    traffic_status = check_traffic(current_lat, current_lon)
                    if traffic_status == 'heavy':
                        await manager.send_personal_message(
                            "Cảnh báo: Đoạn đường sắp tới đang kẹt xe.",
                            user_id
                        )
           
            except json.JSONDecodeError:
                await manager.send_personal_message("Invalid message format", user_id)
                
    except Exception as e:
        logging.error(f"WebSocket error: {str(e)}")
    finally:
        manager.disconnect(websocket, user_id)

# Đặt base prompt cho agent theo user và agent_id
# main.py

@app.put("/agent/{agent_id}/base-prompt")
async def set_base_prompt(
        agent_id: int,
        request: BasePromptRequest,
        current_user: User = Depends(get_current_user),
        token: str = Depends(oauth2_scheme)
):
    print("break 1")
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

        print("break 2")

        # Lấy hoặc tạo agent cho user và agent_id
        agent = get_or_create_agent(current_user.user_id, agent_id)

        print("break 3")

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
        current_user: User = Depends(get_current_user)
):
    # Kiểm tra agent_id hợp lệ
    if agent_id not in [1, 2, 3]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Invalid agent ID", "code": 400}
        )

    agent = get_or_create_agent(current_user.user_id, agent_id)
    return {"base_prompt": agent.base_prompt}


# API chat agent
@app.post("/chat/agent/{agent_id}")
async def chat_agent(
        agent_id: int,
        request: ChatRequest,
        current_user: User = Depends(get_current_user),
        token: str = Depends(oauth2_scheme)
):
    # Kiểm tra agent_id hợp lệ
    if agent_id not in [1, 2, 3]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent không tồn tại."
        )

    agent = get_or_create_agent(current_user.user_id, agent_id)
    try:
        response = agent.chat(request.query, token)
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
