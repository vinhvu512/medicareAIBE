from sqlalchemy import Column, Integer, String, ForeignKey
from database.session import Base

class ClinicRoom(Base):
    __tablename__ = "clinic_rooms"

    room_id = Column(Integer, primary_key=True, autoincrement=True)
    room_name = Column(String(255), nullable=False)
    room_location = Column(String(255))
    room_image = Column(String(255))
    department_id = Column(Integer, ForeignKey('departments.department_id'))
    hospital_id = Column(Integer, ForeignKey('hospitals.hospital_id'))