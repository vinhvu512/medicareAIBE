from pydantic import BaseModel

class ClinicRoomBase(BaseModel):
    room_name: str
    room_location: str | None = None
    room_image: str | None = None
    department_id: int
    hospital_id: int

class ClinicRoomCreate(ClinicRoomBase):
    pass

class ClinicRoom(ClinicRoomBase):
    room_id: int

    class Config:
        from_attributes = True