from pydantic import BaseModel

class ClinicRoomBase(BaseModel):
    m_room_name: str
    m_room_location: str | None = None
    m_room_image: str | None = None
    m_department_id: int
    m_hospital_id: int

class ClinicRoomCreate(ClinicRoomBase):
    pass

class ClinicRoom(ClinicRoomBase):
    m_room_id: int

    class Config:
        from_attributes = True