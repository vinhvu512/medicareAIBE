from sqlalchemy import Column, Integer, String, ForeignKey
from database.session import Base

class Patient(Base):
    __tablename__ = "patients"

    patient_id = Column(Integer, ForeignKey('users.user_id'), primary_key=True)
    profile_image = Column(String(255))