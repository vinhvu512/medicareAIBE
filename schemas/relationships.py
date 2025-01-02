from pydantic import BaseModel
from datetime import date
from enum import Enum

class RelationshipStatusEnum(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    PENDING = "Pending"
    TERMINATED = "Terminated"

class PatientDoctorRelationshipBase(BaseModel):
    m_patient_id: int
    m_doctor_id: int
    m_relationship_type: str
    m_relationship_status: RelationshipStatusEnum
    m_relationship_start_date: date
    m_relationship_end_date: date | None = None

class PatientDoctorRelationshipCreate(PatientDoctorRelationshipBase):
    pass

class PatientDoctorRelationship(PatientDoctorRelationshipBase):
    m_relationship_id: int

    class Config:
        from_attributes = True

class PatientHospitalBase(BaseModel):
    m_patient_id: int
    m_hospital_id: int
    m_relationship_type: str | None = None
    m_start_date: date
    m_end_date: date | None = None

class PatientHospitalCreate(PatientHospitalBase):
    pass

class PatientHospital(PatientHospitalBase):
    m_relationship_id: int

    class Config:
        from_attributes = True

class DoctorHospitalBase(BaseModel):
    m_doctor_id: int
    m_hospital_id: int
    m_work_schedule: str | None = None
    m_start_date: date
    m_end_date: date | None = None
    m_relationship_status: RelationshipStatusEnum | None = None

class DoctorHospitalCreate(DoctorHospitalBase):
    pass

class DoctorHospital(DoctorHospitalBase):
    m_relationship_id: int

    class Config:
        from_attributes = True