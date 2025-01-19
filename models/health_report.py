from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime, JSON
from sqlalchemy.orm import relationship
from database.session import Base
from datetime import datetime

class HealthReport(Base):
    __tablename__ = "health_reports"

    report_id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.appointment_id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"), nullable=False)
    chat_content = Column(Text, nullable=False)  # Có thể lưu trữ dưới dạng JSON nếu cần
    prediction_results = Column(JSON, nullable=False)  # Lưu trữ kết quả dự đoán dưới dạng JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Quan hệ với các bảng khác
    appointment = relationship("Appointment", back_populates="health_reports")
    patient = relationship("Patient", back_populates="health_reports")
