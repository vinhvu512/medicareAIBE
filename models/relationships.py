from sqlalchemy import Column, Integer, String, ForeignKey, Date, Enum
from database.session import Base
import enum

class RelationshipStatusEnum(str, enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    PENDING = "Pending"
    TERMINATED = "Terminated"

class PatientDoctorRelationship(Base):
    __tablename__ = "patient_doctor_relationships"

    m_relationship_id = Column(Integer, primary_key=True, autoincrement=True)
    m_patient_id = Column(Integer, ForeignKey('patients.m_patient_id'))
    m_doctor_id = Column(Integer, ForeignKey('doctors.m_doctor_id'))
    m_relationship_type = Column(String(50), nullable=False)
    m_relationship_status = Column(Enum(RelationshipStatusEnum), nullable=False)
    m_relationship_start_date = Column(Date, nullable=False)
    m_relationship_end_date = Column(Date)

class PatientHospital(Base):
    __tablename__ = "patient_hospitals"

    m_relationship_id = Column(Integer, primary_key=True, autoincrement=True)
    m_patient_id = Column(Integer, ForeignKey('patients.m_patient_id'))
    m_hospital_id = Column(Integer, ForeignKey('hospitals.m_hospital_id'))
    m_relationship_type = Column(String(50))
    m_start_date = Column(Date, nullable=False)
    m_end_date = Column(Date)

class DoctorHospital(Base):
    __tablename__ = "doctor_hospitals"

    m_relationship_id = Column(Integer, primary_key=True, autoincrement=True)
    m_doctor_id = Column(Integer, ForeignKey('doctors.m_doctor_id'))
    m_hospital_id = Column(Integer, ForeignKey('hospitals.m_hospital_id'))
    m_work_schedule = Column(String(255))
    m_start_date = Column(Date, nullable=False)
    m_end_date = Column(Date)
    m_relationship_status = Column(Enum(RelationshipStatusEnum))