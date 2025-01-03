from pydantic import BaseModel
from datetime import date
from enum import Enum

class RelationshipStatusEnum(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    PENDING = "Pending"
    TERMINATED = "Terminated"

class PatientDoctorRelationshipBase(BaseModel):
    patient_id: int
    doctor_id: int
    relationship_type: str
    relationship_status: RelationshipStatusEnum
    relationship_start_date: date
    relationship_end_date: date | None = None

class PatientDoctorRelationshipCreate(PatientDoctorRelationshipBase):
    pass

class PatientDoctorRelationship(PatientDoctorRelationshipBase):
    relationship_id: int

    class Config:
        from_attributes = True

class PatientHospitalBase(BaseModel):
    patient_id: int
    hospital_id: int
    relationship_type: str | None = None
    start_date: date
    end_date: date | None = None

class PatientHospitalCreate(PatientHospitalBase):
    pass

class PatientHospital(PatientHospitalBase):
    relationship_id: int

    class Config:
        from_attributes = True

class DoctorHospitalBase(BaseModel):
    doctor_id: int
    hospital_id: int
    work_schedule: str | None = None
    start_date: date
    end_date: date | None = None
    relationship_status: RelationshipStatusEnum | None = None

class DoctorHospitalCreate(DoctorHospitalBase):
    pass

class DoctorHospital(DoctorHospitalBase):
    relationship_id: int

    class Config:
        from_attributes = True