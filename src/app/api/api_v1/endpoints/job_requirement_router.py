from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.schemas.skill import RequirementCreate
from app.services import requirement_service
from app.sql_app.database import get_db
from app.utils.process_request import process_request

router = APIRouter()


@router.post("/", description="Create a new job requirement.")
def create_job_requirement(
    job_requirement_data: RequirementCreate, db: Session = Depends(get_db)
) -> JSONResponse:
    def _create_job_requirement():
        # TODO Add Company ID when authentication is implemented
        return requirement_service.create(
            company_id=None, requirement_data=job_requirement_data, db=db
        )

    return process_request(
        get_entities_fn=_create_job_requirement,
        status_code=status.HTTP_201_CREATED,
        not_found_err_msg="Job Requirement not created",
    )
