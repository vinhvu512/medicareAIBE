from sqlalchemy import Column, Integer, String, ForeignKey
from database.session import Base

class Department(Base):
    __tablename__ = "departments"

    m_department_id = Column(Integer, primary_key=True, autoincrement=True)
    m_department_name = Column(String(255), nullable=False)
    m_department_location = Column(String(255))
    m_hospital_id = Column(Integer, ForeignKey('hospitals.m_hospital_id'))