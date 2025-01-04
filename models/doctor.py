from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint, JSON
from database.session import Base
from sqlalchemy.orm import relationship

class Doctor(Base):
    __tablename__ = "doctors"

    doctor_id = Column(Integer, ForeignKey('users.user_id'), primary_key=True)
    doctor_specialty = Column(String(255), nullable=False)
    doctor_experience = Column(Integer, nullable=False, default=0)
    profile_image = Column(String(255))
    # New column to store schedule as JSON
    weekly_schedule = Column(JSON, default=lambda: {day: [] for day in WeekDay})

    user = relationship(
        "User",
        backref="doctor",
        uselist=False,
        lazy='joined'
    )

    __table_args__ = (
        CheckConstraint('doctor_experience >= 0', name='check_experience_positive'),
    )