from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from database.session import get_db
from models.department import Department
from schemas.department import Department as DepartmentSchema

router = APIRouter()

@router.get("/search", response_model=List[DepartmentSchema])
async def search_departments(
    hospital_id: int = Query(..., description="Hospital ID to search for departments"),
    db: Session = Depends(get_db)
):
    """
    Search departments by hospital ID.
    Returns all departments associated with the specified hospital.
    """
    try:
        departments = db.query(Department)\
            .filter(Department.hospital_id == hospital_id)\
            .all()

        if not departments:
            return {
                "code": 404,
                "message": f"No departments found for hospital ID: {hospital_id}",
                "data": []
            }

        department_list = [
            {
                "department_id": department.department_id,
                "department_name": department.department_name,
                "department_location": department.department_location,
                "hospital_id": department.hospital_id
            }
            for department in departments
        ]

        return {
            "code": 200,
            "message": "Departments retrieved successfully",
            "data": department_list
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail={
                "code": 500,
                "message": f"Error searching departments: {str(e)}"
            }
        )