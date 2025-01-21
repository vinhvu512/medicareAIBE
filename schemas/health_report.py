from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class HealthReportCreate(BaseModel):
    appointment_id: int
    chat_content: str = "Đau tay"   # Hoặc có thể là dict nếu lưu trữ dưới dạng JSON
    # Bạn có thể thêm các trường khác nếu cần

class PredictionResult(BaseModel):
    disease_name: str
    probability: float

class HealthReportResponse(BaseModel):
    report_id: int
    appointment_id: int
    patient_id: int
    chat_content: str
    prediction_results: Any
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
