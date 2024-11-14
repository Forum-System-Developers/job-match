from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.app.schemas.job_ad import JobAd
from src.app.services import job_ad_service
from src.app.sql_app.database import get_db
from src.app.utils.process_request import process_request

router = APIRouter()


@router.get(
    "/{id}",
    response_model=JobAd,
    description="Retrieve a job advertisement by its unique identifier.",
)
def get_job_ad_by_id(id: UUID, db: Session = Depends(get_db)) -> JobAd:
    def _get_job_ad_by_id():
        return job_ad_service.get_by_id(id=id, db=db)

    return process_request(
        get_entities_fn=_get_job_ad_by_id,
        not_found_err_msg=f"Job Ad with id {id} not found",
    )
