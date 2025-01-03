from sqlalchemy import Column, Integer, String
from database.session import Base

class Hospital(Base):
    __tablename__ = "hospitals"

    hospital_id = Column(Integer, primary_key=True, autoincrement=True)
    hospital_name = Column(String(255), nullable=False)
    hospital_address = Column(String(255))
    hospital_phone = Column(String(15))
    hospital_email = Column(String(255))
    hospital_image = Column(String(255))