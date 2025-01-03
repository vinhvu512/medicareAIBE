from pydantic import BaseModel

class DepartmentBase(BaseModel):
    department_name: str
    department_location: str | None = None
    hospital_id: int

class DepartmentCreate(DepartmentBase):
    pass

class Department(DepartmentBase):
    department_id: int

    class Config:
        from_attributes = True