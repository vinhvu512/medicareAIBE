from sqlalchemy import Column, Integer, String, Date, Enum
from database.session import Base
import enum

class GenderEnum(str, enum.Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"

class UserTypeEnum(str, enum.Enum):
    DOCTOR = "Doctor"
    PATIENT = "Patient"

class User(Base):
    __tablename__ = "users"

    m_user_id = Column(Integer, primary_key=True, autoincrement=True)
    m_username = Column(String(255), nullable=False, unique=True)
    m_email = Column(String(255), nullable=False, unique=True)
    m_password = Column(String(255), nullable=False, server_default='1234')
    m_user_type = Column(Enum(UserTypeEnum), nullable=False)
    m_fullname = Column(String(255), nullable=False)
    m_date_of_birth = Column(Date, nullable=False)
    m_gender = Column(Enum(GenderEnum))
    m_address = Column(String(255))
    m_phone = Column(String(15))
    m_profile_image = Column(String(255))