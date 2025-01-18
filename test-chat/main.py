# -*- coding: utf-8 -*-
# backend/main.py

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import json
from deepgram import DeepgramClient, PrerecordedOptions, FileSource
import os
from typing import List, Tuple
import math
from datetime import datetime
import asyncio
from dotenv import load_dotenv

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

with open('traffic_data.json', 'r', encoding='utf-8') as f:
    traffic_data = json.load(f)

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371000  # Bán kính Trái Đất tính bằng mét
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2) ** 2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

def check_traffic(current_lat, current_lon):
    """
    Kiểm tra xem có đoạn đường sắp tới đang kẹt xe hay không.

    Parameters:
    - current_lat, current_lon: Vĩ độ và kinh độ hiện tại của xe

    Returns:
    - 'heavy' nếu có kẹt xe, 'clear' nếu không có
    """
    now = datetime.now()
    current_hour = now.hour
    current_minute = now.minute

    # Xác định khoảng thời gian hiện tại
    time_period = None
    if 7 <= current_hour < 9:
        time_period = "7h-9h"
    elif 9 <= current_hour < 11:
        time_period = "9h-11h"
    elif 11 <= current_hour < 13:
        time_period = "11h-13h"
    elif 13 <= current_hour < 15:
        time_period = "13h-15h"
    elif 15 <= current_hour < 17:
        time_period = "15h-17h"
    elif 17 <= current_hour < 19:
        time_period = "17h-19h"
    elif 19 <= current_hour < 21:
        time_period = "19h-21h"
    else:
        # Ngoài các khoảng thời gian đã định, không có kẹt xe
        return 'clear'

    # Lấy danh sách các điểm kẹt xe trong khoảng thời gian hiện tại
    congestion_points = traffic_data.get(time_period, [])

    # Chỉ xem xét các điểm kẹt xe với trạng thái 'Cao' hoặc 'Rất cao'
    relevant_congestion_points = [
        point for point in congestion_points
        if point['status'].lower() in ['cao', 'rất cao']
    ]

    # Kiểm tra xem vị trí hiện tại có gần bất kỳ điểm kẹt xe nào không
    for point in relevant_congestion_points:
        distance = haversine_distance(
            current_lat, current_lon,
            point['latitude'], point['longitude']
        )
        if distance <= 700:
            return 'heavy'

    return 'clear'

def process_message(message: str):
    if "tìm đường" in message.lower():
        return "Tôi sẽ tìm đường đi cho bạn."
    else:
        return "Xin lỗi, tôi không hiểu yêu cầu của bạn."

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                print("Receive Message: ", message)
                if message['type'] == 'location':
                    print("Receive location")
                    latitude = message['latitude']
                    longitude = message['longitude']
                    traffic_status = check_traffic(latitude, longitude)
                    if traffic_status == 'heavy':
                        # alert_message = json.dumps({
                        #     "type": "traffic_alert",
                        #     "message": "Cảnh báo: Đoạn đường sắp tới đang kẹt xe."
                        # })
                        # await manager.send_personal_message(alert_message, websocket)
                        await manager.send_personal_message("Cảnh báo: Đoạn đường sắp tới đang kẹt xe.", websocket)
                elif message['type'] == 'text':
                    response = process_message(message['text'])
                    if response:
                        await manager.send_personal_message(response, websocket)
            except json.JSONDecodeError:
                response = process_message(data)
                if response:
                    await manager.send_personal_message(response, websocket)
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
