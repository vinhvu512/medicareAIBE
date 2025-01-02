from sqlalchemy import Column, Integer, String, ForeignKey
from database.session import Base

class ClinicRoom(Base):
    __tablename__ = "clinic_rooms"

    m_room_id = Column(Integer, primary_key=True, autoincrement=True)
    m_room_name = Column(String(255), nullable=False)
    m_room_location = Column(String(255))
    m_room_image = Column(String(255))
    m_department_id = Column(Integer, ForeignKey('departments.m_department_id'))
    m_hospital_id = Column(Integer, ForeignKey('hospitals.m_hospital_id'))