# backend/main.py

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import json
import whisper

app = FastAPI()

# Cấu hình CORS để cho phép frontend kết nối
origins = [
    "*",  # Trong sản phẩm thực tế, hãy chỉ định domain cụ thể
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Quản lý các kết nối WebSocket
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

# Tải mô hình Whisper
model = whisper.load_model("base")  # Bạn có thể chọn các mô hình khác như "tiny", "small", "medium", "large"

def check_traffic(latitude, longitude):
    # Triển khai logic kiểm tra giao thông thực tế
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
        # Đọc nội dung tệp âm thanh
        audio_bytes = await file.read()

        # Lưu file tạm thời để Whisper có thể xử lý
        temp_file = "temp_audio.wav"
        with open(temp_file, "wb") as f:
            f.write(audio_bytes)

        # Sử dụng Whisper để chuyển đổi âm thanh thành văn bản
        result = model.transcribe(temp_file, language="vi")

        # Kiểm tra kết quả trả về
        if isinstance(result, dict) and "text" in result:
            transcript = result["text"]
        else:
            transcript = ""

        # Xóa file tạm
        import os
        if os.path.exists(temp_file):
            os.remove(temp_file)

        return {"text": transcript}
    except Exception as e:
        print(f"Error in speech_to_text: {e}")
        return {"text": ""}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=4000, reload=True)
