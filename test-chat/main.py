# -*- coding: utf-8 -*-
# backend/main.py

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import json
from deepgram import DeepgramClient, PrerecordedOptions, FileSource
import os
import asyncio
from dotenv import load_dotenv

from apis.authenticate.authenticate import get_current_user, verify_token
from agent.main import get_or_create_agent  # Import the missing function
load_dotenv()

app = FastAPI()

# CORS Configuration to allow frontend connections
origins = [
    "*",  # In production, specify the exact domains
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Manage WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print("Client connected.")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print("Client disconnected.")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

from deepgram import Deepgram

# Initialize Deepgram Client
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
if not DEEPGRAM_API_KEY:
    raise ValueError("DEEPGRAM_API_KEY environment variable is not set")
  
deepgram = DeepgramClient()

def check_traffic(latitude, longitude):
    # Implement real traffic checking logic
    if int(latitude * 100) % 2 == 1:
        return "heavy"
    return "smooth"

def process_message(message: str):
    if "tìm đường" in message.lower():
        return "Tôi sẽ tìm đường đi cho bạn."
    else:
        return "Xin lỗi, tôi không hiểu yêu cầu của bạn."

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Get current user from token
        token = websocket.headers.get("Authorization")
        if not token:
            await websocket.close(code=4001, reason="Missing authentication token")
            return
            
        try:
            # Get user from token
            current_user = get_current_user(token)
            if not current_user:
                await websocket.close(code=4002, reason="Invalid authentication")
                return
                
            # Create agent for this user (using agent 1)
            agent = get_or_create_agent(current_user.user_id, 1)
            
            while True:
                data = await websocket.receive_text()
                try:
                    message = json.loads(data)
                    print("Receive Message: ", message)
                    
                    # Check if message is location data
                    if 'type' in message and message['type'] == 'location':
                        # Handle location message
                        latitude = message['latitude']
                        longitude = message['longitude']
                        traffic_status = check_traffic(latitude, longitude)
                        if traffic_status == 'heavy':
                            alert_message = json.dumps({
                                "type": "traffic_alert", 
                                "message": "Cảnh báo: Đoạn đường sắp tới đang kẹt xe."
                            })
                            C
                            agent.setMem("traffic_alert", "true")
                            await manager.send_personal_message(alert_message, websocket)
                    else:
                        # All other messages handled by agent
                        response = agent.chat(data, token)
                        if response:
                            await manager.send_personal_message(response, websocket)
                            
                except json.JSONDecodeError:
                    # Handle plain text message using agent
                    response = agent.chat(data, token)
                    if response:
                        await manager.send_personal_message(response, websocket)
                        
        except Exception as e:
            await websocket.close(code=4003, reason=f"Error: {str(e)}")
            return
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/speech-to-text")
async def speech_to_text(file: UploadFile = File(...)):
    try:
        # Đọc file audio từ upload
        audio_bytes = await file.read()

        # Chuẩn bị payload và options
        payload: FileSource = {"buffer": audio_bytes}
        options = PrerecordedOptions(
            model="nova-2",        # Hoặc mô hình phù hợp
            language="vi",         # Tiếng Việt
            smart_format=True,     # Định dạng thông minh
        )

        file_response = deepgram.listen.rest.v("1").transcribe_file(payload, options)
        response_dict = file_response.to_dict()

        # Extract main transcript and metadata
        channel = response_dict.get('results', {}).get('channels', [])[0]
        alternative = channel.get('alternatives', [])[0]
        transcript = alternative.get('transcript', '')
        confidence = alternative.get('confidence', 0)
        duration = response_dict.get('metadata', {}).get('duration', 0)
        
        # Extract word-level details
        words = [{
            'word': w.get('punctuated_word', ''),
            'start': w.get('start', 0),
            'end': w.get('end', 0),
            'confidence': w.get('confidence', 0)
        } for w in alternative.get('words', [])]

        return {
            "text": transcript,
            "confidence": confidence,
            "duration": duration,
            "words": words
        }

    except Exception as e:
        print(f"Error in speech_to_text: {str(e)}")
        return {
            "text": "",
            "confidence": 0,
            "duration": 0,
            "words": []
        }



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=4000, reload=True)
