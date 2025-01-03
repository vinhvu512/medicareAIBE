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

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False, server_default='1234')
    user_type = Column(Enum(UserTypeEnum), nullable=False)
    fullname = Column(String(255), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(Enum(GenderEnum))
    address = Column(String(255))
    phone = Column(String(15))
    profile_image = Column(String(255))