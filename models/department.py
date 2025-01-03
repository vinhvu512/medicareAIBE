from sqlalchemy import Column, Integer, String, ForeignKey
from database.session import Base

class Department(Base):
    __tablename__ = "departments"

    department_id = Column(Integer, primary_key=True, autoincrement=True)
    department_name = Column(String(255), nullable=False)
    department_location = Column(String(255))
    hospital_id = Column(Integer, ForeignKey('hospitals.hospital_id'))