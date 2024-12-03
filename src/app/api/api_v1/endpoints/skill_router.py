from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.schemas.company import CompanyResponse
from app.schemas.skill import SkillCreate
from app.services import skill_service
from app.services.auth_service import require_company_role
from app.sql_app.database import get_db
from app.utils.processors import process_request

router = APIRouter()


@router.post("/", description="Create a new job requirement.")
def create_skill(
    skill_data: SkillCreate,
    company: CompanyResponse = Depends(require_company_role),
    db: Session = Depends(get_db),
) -> JSONResponse:
    def _create_job_requirement():
        return skill_service.add_pending_skill(
            company_id=company.id, skill_data=skill_data, db=db
        )

    return process_request(
        get_entities_fn=_create_job_requirement,
        status_code=status.HTTP_201_CREATED,
        not_found_err_msg="Job Requirement not created",
    )
