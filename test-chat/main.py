# backend/main.py

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import json
from deepgram import DeepgramClient, PrerecordedOptions, FileSource
import os
import asyncio

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

# Initialize Deepgram Client
DEEPGRAM_API_KEY = "YOUR_DEEPGRAM_API_KEY"  # Replace with your actual Deepgram API key
deepgram = DeepgramClient(api_key=DEEPGRAM_API_KEY)

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
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                print("Receive Message: ", message)
                if message['type'] == 'location':
                    latitude = message['latitude']
                    longitude = message['longitude']
                    traffic_status = check_traffic(latitude, longitude)
                    if traffic_status == 'heavy':
                        alert_message = json.dumps({
                            "type": "traffic_alert",
                            "message": "Cảnh báo: Đoạn đường sắp tới đang kẹt xe."
                        })
                        await manager.send_personal_message(alert_message, websocket)
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
        # Read the uploaded audio file
        audio_bytes = await file.read()

        # Prepare the file source for Deepgram
        payload: FileSource = {
            "buffer": audio_bytes,
        }

        # Set transcription options
        options = PrerecordedOptions(
            model="nova-2",       # Use appropriate model as per Deepgram's documentation
            language="vi",        # Vietnamese language code
            smart_format=True,    # Enables smart formatting
        )

        # Perform transcription using Deepgram
        response = await deepgram.transcription.pre_recorded(payload, options)

        # Extract the transcript from the response
        if 'results' in response and 'channels' in response['results']:
            transcript = ""
            for channel in response['results']['channels']:
                for alternative in channel.get('alternatives', []):
                    transcript += alternative.get('transcript', '') + " "
            transcript = transcript.strip()
        else:
            transcript = ""

        return {"text": transcript}
    except Exception as e:
        print(f"Error in speech_to_text: {e}")
        return {"text": ""}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=4000, reload=True)
