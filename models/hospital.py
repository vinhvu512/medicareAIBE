from sqlalchemy import Column, Integer, String
from database.session import Base

class Hospital(Base):
    __tablename__ = "hospitals"

    m_hospital_id = Column(Integer, primary_key=True, autoincrement=True)
    m_hospital_name = Column(String(255), nullable=False)
    m_hospital_address = Column(String(255))
    m_hospital_phone = Column(String(15))
    m_hospital_email = Column(String(255))
    m_hospital_image = Column(String(255))