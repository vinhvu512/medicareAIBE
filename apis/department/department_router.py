from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from database.session import get_db
from models.department import Department
from schemas.department import Department as DepartmentSchema

router = APIRouter()

@router.get("/{department_id}", response_model=DepartmentSchema)
async def get_department_by_id(
    department_id: int,
    db: Session = Depends(get_db)
):
    """
    Get department information by department_id.
    Returns department's details.
    """
    try:
        department = db.query(Department)\
            .filter(Department.department_id == department_id)\
            .first()

        if not department:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": f"Department with ID {department_id} not found",
                    "code": 404
                }
            )

        return department

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"Error fetching department: {str(e)}",
                "code": 500
            }
        )

@router.get("/search/{hospital_id}", response_model=List[DepartmentSchema])
async def search_departments(
    hospital_id: int,
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
            raise HTTPException(
                status_code=404,
                detail={
                    "error": f"No departments found for hospital ID: {hospital_id}",
                    "code": 404
                }
            )

        return departments

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail={
                "error": f"Error searching departments: {str(e)}",
                "code": 500
            }
        )