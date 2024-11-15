from typing import Union
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from src.app.schemas.job_ad import JobAdResponse
from src.app.services import job_ad_service
from src.app.sql_app.database import get_db
from src.app.utils.process_request import process_request

router = APIRouter()


@router.get(
    "/{id}",
    response_model=Union[JobAdResponse, JSONResponse],
    description="Retrieve a job advertisement by its unique identifier.",
)
def get_job_ad_by_id(
    id: UUID, db: Session = Depends(get_db)
) -> BaseModel | JSONResponse:
    def _get_job_ad_by_id():
        return job_ad_service.get_by_id(id=id, db=db)

    return process_request(
        get_entities_fn=_get_job_ad_by_id,
        not_found_err_msg=f"Job Ad with id {id} not found",
    )
