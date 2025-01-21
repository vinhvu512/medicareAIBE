
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

from difflib import SequenceMatcher

import nest_asyncio
nest_asyncio.apply()

import httpx

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
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        print(f"Client {client_id} connected")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            print(f"Client {client_id} disconnected")

    async def send_personal_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            try:
                # Ensure proper JSON encoding of Unicode characters
                if isinstance(message, str):
                    message = json.dumps(json.loads(message), ensure_ascii=False)
                await self.active_connections[client_id].send_text(message)
                print(f"Sent to {client_id}: {message}")
            except Exception as e:
                print(f"Error sending message to {client_id}: {str(e)}")

manager = ConnectionManager()

async def first_route_tool(user_id: str):
    try:
        url = "https://api.mapbox.com/directions/v5/mapbox/driving/106.658339,10.770304;106.648938,10.795434;106.63777,10.801162"
        params = {
            "alternatives": "true",
            "geometries": "geojson",
            "language": "en", 
            "overview": "full",
            "steps": "true",
            "access_token": "pk.eyJ1IjoibWluaGhpZXUxMSIsImEiOiJjbTU4OWdkaXA0MXg3Mmtwa2ZnMXBnbGpvIn0.VcU6Q0FhEgmHMIjSHhu2gA"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            route_data = response.json()

            await manager.send_personal_message(
                json.dumps({
                    "event": "route_data",
                    "data": route_data
                }),
                user_id
            )
            print(f"Sent route data to user {user_id}")
    except Exception as e:
        logging.error(f"Error in sample_tool: {str(e)}")
        await manager.send_personal_message(
            json.dumps({
                "event": "error",
                "data": str(e)
            }),
            user_id
        )

async def new_route_tool(user_id: str):

    try:
        url = "https://api.mapbox.com/directions/v5/mapbox/driving/106.653603,10.786561;106.650633,10.788560;106.63777,10.801162"
        params = {
            "alternatives": "true",
            "geometries": "geojson",
            "language": "en", 
            "overview": "full",
            "steps": "true",
            "access_token": "pk.eyJ1IjoibWluaGhpZXUxMSIsImEiOiJjbTU4OWdkaXA0MXg3Mmtwa2ZnMXBnbGpvIn0.VcU6Q0FhEgmHMIjSHhu2gA"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            route_data = response.json()

            await manager.send_personal_message(
                json.dumps({
                    "event": "route_data",
                    "data": route_data
                }),
                user_id
            )
            print(f"Sent route data to user {user_id}")
    except Exception as e:
        logging.error(f"Error in sample_tool: {str(e)}")
        await manager.send_personal_message(
            json.dumps({
                "event": "error",
                "data": str(e)
            }),
            user_id
        )

script_responses = {
    # Module 1: Route-related responses
    "Bạn hãy giúp tôi tạo đường đi từ vị trí hiện tại đến chợ Võ Thành Trang": {
        "response": "Có phải bạn muốn đến chợ Võ Thành Trang ở địa chỉ 15 đường Trường Chinh, Phường 13, Tân Bình, Hồ Chí Minh không?",
        "action": None
    },
    "Đúng vậy": {
        "response": "Tôi vừa tạo đường đi cho bạn! Nếu có thêm yêu cầu nào, bạn hãy gọi cho tôi để hỗ trợ bạn.",
        "action": first_route_tool
    },
    "Có, bạn hãy đổi cho tôi": {
        "response": "Tôi vừa cho bạn một tuyến đường mới đi qua đường Phạm Phú Thứ để tránh kẹt xe! Nếu bạn cần giúp đỡ thêm hãy nói cho tôi biết.",
        "action": new_route_tool
    },

    # Module 2: Hospital appointment and diagnosis
    "Tôi muốn đặt lịch hẹn với bác sĩ Nguyễn Văn Thành ở bệnh viện Trưng Vương": {
        "response": "Bạn có thể cho tôi biết ngày và giờ bạn muốn đặt lịch hẹn không?",
        "action": None
    },
    "Tôi muốn khám lúc 8h ngày 22/01/2024": {
        "response": "Lịch hẹn của bạn đã được đặt với bác sĩ Nguyễn Văn Thành vào lúc 8h ngày 22/01/2024. Sau đây, để có thể chuẩn đoán sơ bộ, bạn có thể cho tôi biết các triệu chứng của bạn được không?",
        "action": None
    },
    "Tôi thấy ngứa và đỏ da ở cổ tay, da hơi khô và tróc vảy.": {
        "response": "Triệu chứng này xuất hiện khi nào? Có liên quan đến điều gì không?",
        "action": None
    },
    "Vài ngày trước, sau khi tôi đeo một chiếc vòng tay mới.": {
        "response": "Cảm ơn bạn đã chia sẻ. Bạn có thấy mụn nước nhỏ hoặc vùng da bị tróc vảy không?",
        "action": None
    },
    "Có một vài mụn nước nhỏ, và da hơi khô.": {
        "response": "Rất có thể bạn đang gặp phải tình trạng viêm da tiếp xúc dị ứng. Điều này xảy ra khi da của bạn phản ứng với một chất gây dị ứng, ví dụ như kim loại trong chiếc vòng tay.",
        "action": None
    },
    "Vậy tôi cần làm gì ?": {
        "response": "Đây là một số gợi ý bạn có thể thử:\n\n1. Tháo vòng tay ra ngay lập tức để tránh tiếp xúc thêm với chất gây dị ứng.\n2. Rửa vùng da bị ảnh hưởng bằng nước sạch và xà phòng dịu nhẹ.\n3. Bôi kem dưỡng ẩm không hương liệu để làm dịu da.\n4. Nếu ngứa nhiều, bạn có thể sử dụng kem chứa corticosteroid nhẹ (nếu có sẵn, theo chỉ định của dược sĩ).",
        "action": None
    },
    "Cảm ơn bạn!": {
        "response": "Rất vui vì tôi có thể giúp bạn! Hãy theo dõi tình trạng của mình và chúc bạn sớm khỏe lại!",
        "action": None
    }
}

def get_script_match(query: str, threshold=0.8):
    max_ratio = 0
    matched_script = None
    
    for script in script_responses.keys():
        ratio = SequenceMatcher(None, query.lower(), script.lower()).ratio()
        if ratio > max_ratio and ratio >= threshold:
            max_ratio = ratio
            matched_script = script
    return matched_script

# Giả lập cơ sở dữ liệu lưu trữ agent cho từng user và agent_id
user_agents: Dict[str, Dict[int, AgentService]] = {}
user_agents_lock = threading.Lock()


# Model cho request chat
class ChatRequest(BaseModel):
    query: str


# Model cho request đặt base prompt
class BasePromptRequest(BaseModel):
    prompt: str


async def get_or_create_agent(user_id: int, agent_id: int) -> AgentService:
    print("break 2.1")

    with user_agents_lock:
        if user_id not in user_agents:
            user_agents[user_id] = {}
            logging.info(f"Initialized agent dictionary for user: {user_id}")
        if agent_id not in user_agents[user_id]:
            user_agents[user_id][agent_id] = AgentService(
                agent_id=agent_id,
                user_id=user_id,
                websocket_manager=manager
            )
            logging.info(f"New agent {agent_id} created for user: {user_id}")
            logging.debug(f"Current user_agents: {user_agents}")
        else:
            logging.info(f"Agent {agent_id} retrieved for user: {user_id}")
    return user_agents[user_id][agent_id]

# WebSocket endpoint for Agent 1
@app.websocket("/ws/agent1/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
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
                            json.dumps({
                                "event": "caution",
                                "data": "Sắp tới đoạn đường kẹt xe, bạn có muốn tôi gợi ý tuyến đường mới không"
                            }),
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
        agent = await get_or_create_agent(current_user.user_id, agent_id)

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
    agent = await get_or_create_agent(current_user.user_id, agent_id)
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

    agent = await get_or_create_agent(current_user.user_id, agent_id)



    try:
        # Dummy chat
        # Check script match
        matched_script = get_script_match(request.query)
        if matched_script:
            script_data = script_responses[matched_script]
            if script_data["action"]:
                await script_data["action"](current_user.user_id)
            return JSONResponse(content={"response": script_data["response"]})

        # Real chat
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
