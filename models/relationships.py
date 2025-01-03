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

    relationship_id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey('patients.patient_id'))
    doctor_id = Column(Integer, ForeignKey('doctors.doctor_id'))
    relationship_type = Column(String(50), nullable=False)
    relationship_status = Column(Enum(RelationshipStatusEnum), nullable=False)
    relationship_start_date = Column(Date, nullable=False)
    relationship_end_date = Column(Date)

class PatientHospital(Base):
    __tablename__ = "patient_hospitals"

    relationship_id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey('patients.patient_id'))
    hospital_id = Column(Integer, ForeignKey('hospitals.hospital_id'))
    relationship_type = Column(String(50))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)

class DoctorHospital(Base):
    __tablename__ = "doctor_hospitals"

    relationship_id = Column(Integer, primary_key=True, autoincrement=True)
    doctor_id = Column(Integer, ForeignKey('doctors.doctor_id'))
    hospital_id = Column(Integer, ForeignKey('hospitals.hospital_id'))
    work_schedule = Column(String(255))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    relationship_status = Column(Enum(RelationshipStatusEnum))