from pydantic import BaseModel

class DepartmentBase(BaseModel):
    m_department_name: str
    m_department_location: str | None = None
    m_hospital_id: int

class DepartmentCreate(DepartmentBase):
    pass

class Department(DepartmentBase):
    m_department_id: int

    class Config:
        from_attributes = True