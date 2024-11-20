from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.schemas.common import FilterParams, JobAdSearchParams
from app.schemas.company import CompanyResponse
from app.schemas.job_ad import JobAdCreate, JobAdUpdate
from app.services import job_ad_service
from app.services.auth_service import get_current_company
from app.sql_app.database import get_db
from app.utils.process_request import process_request

router = APIRouter()


@router.post(
    "/all",
    description="Retrieve all job advertisements.",
)
def get_all_job_ads(
    search_params: JobAdSearchParams,
    filter_params: FilterParams = Depends(),
    db: Session = Depends(get_db),
) -> JSONResponse:
    def _get_all_job_ads():
        return job_ad_service.get_all(
            filter_params=filter_params, search_params=search_params, db=db
        )

    return process_request(
        get_entities_fn=_get_all_job_ads,
        status_code=status.HTTP_200_OK,
        not_found_err_msg="No job ads found",
    )


@router.get(
    "/{job_ad_id}",
    description="Retrieve a job advertisement by its unique identifier.",
)
def get_job_ad_by_id(job_ad_id: UUID, db: Session = Depends(get_db)) -> JSONResponse:
    def _get_job_ad_by_id():
        return job_ad_service.get_by_id(id=job_ad_id, db=db)

    return process_request(
        get_entities_fn=_get_job_ad_by_id,
        status_code=status.HTTP_200_OK,
        not_found_err_msg=f"Job Ad with id {job_ad_id} not found",
    )


@router.post(
    "/",
    description="Create a new job advertisement.",
)
def create_job_ad(
    job_ad_data: JobAdCreate,
    company: CompanyResponse = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> JSONResponse:
    def _create_job_ad():
        return job_ad_service.create(company=company, job_ad_data=job_ad_data, db=db)

    return process_request(
        get_entities_fn=_create_job_ad,
        status_code=status.HTTP_201_CREATED,
        not_found_err_msg="Job Ad not created",
    )


@router.put(
    "/{job_ad_id}",
    description="Update a job advertisement by its unique identifier.",
)
def update_job_ad(
    job_ad_id: UUID,
    job_ad_data: JobAdUpdate,
    company: CompanyResponse = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> JSONResponse:
    def _update_job_ad():
        return job_ad_service.update(
            job_ad_id=job_ad_id, company_id=company.id, job_ad_data=job_ad_data, db=db
        )

    return process_request(
        get_entities_fn=_update_job_ad,
        status_code=status.HTTP_200_OK,
        not_found_err_msg=f"Job Ad with id {job_ad_id} not found",
    )


@router.post(
    "/{job_ad_id}/requirements/{requirement_id}",
    description="Add new job requirements to a job advertisement.",
)
def add_job_ad_requirement(
    job_ad_id: UUID,
    requirement_id: UUID,
    company: CompanyResponse = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> JSONResponse:
    def _add_job_ad_requirements():
        return job_ad_service.add_requirement(
            job_ad_id=job_ad_id,
            requirement_id=requirement_id,
            company_id=company.id,
            db=db,
        )

    return process_request(
        get_entities_fn=_add_job_ad_requirements,
        status_code=status.HTTP_200_OK,
        not_found_err_msg=f"Job Ad with id {job_ad_id} not found",
    )


@router.get(
    "/{job_ad_id}/match-requests",
    description="Retrieve all match requests for a job advertisement.",
)
def get_job_ad_match_requests(
    job_ad_id: UUID,
    company: CompanyResponse = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> JSONResponse:
    def _get_job_ad_requests():
        return job_ad_service.get_match_requests(
            job_ad_id=job_ad_id,
            company_id=company.id,
            db=db,
        )

    return process_request(
        get_entities_fn=_get_job_ad_requests,
        status_code=status.HTTP_200_OK,
        not_found_err_msg=f"No requests found for job ad with id {job_ad_id}",
    )


@router.patch(
    "/{job_ad_id}/job-applications/{job_application_id}/match-requests",
    description="Accept a match request for a job advertisement.",
)
def accept_job_ad_match_request(
    job_ad_id: UUID,
    job_application_id: UUID,
    company: CompanyResponse = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> JSONResponse:
    def _accept_job_ad_request():
        return job_ad_service.accept_match_request(
            job_ad_id=job_ad_id,
            job_application_id=job_application_id,
            company_id=company.id,
            db=db,
        )

    return process_request(
        get_entities_fn=_accept_job_ad_request,
        status_code=status.HTTP_200_OK,
        not_found_err_msg=f"Match request not found for job ad with id {job_ad_id}",
    )


@router.post(
    "/{job_ad_id}/job-applications/{job_application_id}/match-requests",
    description="Send a match request to a job advertisement.",
)
def send_job_ad_match_request(
    job_ad_id: UUID,
    job_application_id: UUID,
    company: CompanyResponse = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> JSONResponse:
    def _send_job_ad_request():
        return job_ad_service.send_match_request(
            job_ad_id=job_ad_id,
            job_application_id=job_application_id,
            company_id=company.id,
            db=db,
        )

    return process_request(
        get_entities_fn=_send_job_ad_request,
        status_code=status.HTTP_200_OK,
        not_found_err_msg=f"Match request not sent for job ad with id {job_ad_id}",
    )
