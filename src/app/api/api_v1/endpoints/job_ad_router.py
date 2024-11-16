from typing import Union
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.schemas.job_ad import JobAdCreate, JobAdResponse, JobAdUpdate
from app.services import job_ad_service
from app.sql_app.database import get_db
from app.utils.process_request import process_request

router = APIRouter()


@router.get(
    "/",
    response_model=list[JobAdResponse],
    description="Retrieve all job advertisements.",
)
def get_all_job_ads(
    skip: int = 0, limit: int = 50, db: Session = Depends(get_db)
) -> Union[BaseModel, JSONResponse]:
    def _get_all_job_ads():
        return job_ad_service.get_all(db=db, skip=skip, limit=limit)

    return process_request(
        get_entities_fn=_get_all_job_ads,
        not_found_err_msg="No job ads found",
    )


@router.get(
    "/{id}",
    description="Retrieve a job advertisement by its unique identifier.",
)
def get_job_ad_by_id(
    id: UUID, db: Session = Depends(get_db)
) -> Union[BaseModel, JSONResponse]:
    def _get_job_ad_by_id():
        return job_ad_service.get_by_id(id=id, db=db)

    return process_request(
        get_entities_fn=_get_job_ad_by_id,
        not_found_err_msg=f"Job Ad with id {id} not found",
    )


@router.post(
    "/",
    response_model=JobAdResponse,
    description="Create a new job advertisement.",
)
def create_job_ad(
    job_ad_data: JobAdCreate, db: Session = Depends(get_db)
) -> Union[BaseModel, JSONResponse]:
    def _create_job_ad():
        return job_ad_service.create(job_ad_data=job_ad_data, db=db)

    return process_request(
        get_entities_fn=_create_job_ad,
        not_found_err_msg="Job Ad not created",
    )


@router.put(
    "/{id}",
    response_model=JobAdResponse,
    description="Update a job advertisement by its unique identifier.",
)
def update_job_ad(
    id: UUID, job_ad_data: JobAdUpdate, db: Session = Depends(get_db)
) -> Union[BaseModel, JSONResponse]:
    def _update_job_ad():
        return job_ad_service.update(id=id, job_ad_data=job_ad_data, db=db)

    return process_request(
        get_entities_fn=_update_job_ad,
        not_found_err_msg=f"Job Ad with id {id} not found",
    )
