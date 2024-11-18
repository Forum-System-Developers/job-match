from uuid import UUID

from fastapi import APIRouter, Depends, Form
from fastapi import status as status_code
from fastapi.responses import JSONResponse
from pydantic import Field
from sqlalchemy.orm import Session

from app.schemas.common import FilterParams, SearchParams
from app.schemas.job_application import JobAplicationBase, JobSearchStatus, JobStatus
from app.schemas.user import UserResponse
from app.services import job_application_service
from app.services.auth_service import get_current_user
from app.sql_app.database import get_db
from app.utils.process_request import process_request

router = APIRouter()


@router.post(
    "/",
    description="Create a Job Application.",
)
def create(
    application_create: JobAplicationBase = Form(
        description="Job Application creation form"
    ),
    is_main: bool = Form(description="Set the Job application as main"),
    application_status: JobStatus = Form(description="Status of the Job Application"),
    user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JSONResponse:
    def _create():
        return job_application_service.create(
            user=user,
            application_create=application_create,
            is_main=is_main,
            application_status=application_status,
            db=db,
        )

    return process_request(
        get_entities_fn=_create,
        status_code=status_code.HTTP_201_CREATED,
        not_found_err_msg="Job application could not be created",
    )


@router.put(
    "/{job_application_id}",
    description="Update a Job Application.",
)
def update(
    job_application_id: UUID,
    application_update: JobAplicationBase = Form(
        description="Job Application update form"
    ),
    is_main: bool = Form(description="Set the Job application as main"),
    application_status: JobStatus = Form(description="Status of the Job Application"),
    user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JSONResponse:
    def _update():
        return job_application_service.update(
            job_application_id=job_application_id,
            user=user,
            application_update=application_update,
            is_main=is_main,
            application_status=application_status,
            db=db,
        )

    return process_request(
        get_entities_fn=_update,
        status_code=status_code.HTTP_200_OK,
        not_found_err_msg="Job application could not be updated",
    )


@router.get(
    "/", description="Get all Job applications (filtered by indicated parameters)"
)
def get_all(
    filter_params: FilterParams = Depends(),
    search_params: SearchParams = Depends(),
    application_status: JobSearchStatus = Form(
        description="Status of the Job Application"
    ),
    user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JSONResponse:
    def _get_all():
        return job_application_service.get_all(
            filter_params=filter_params,
            db=db,
            status=application_status,
            search_params=search_params,
        )

    return process_request(
        get_entities_fn=_get_all,
        status_code=status_code.HTTP_200_OK,
        not_found_err_msg="Could not fetch Job Applications",
    )


@router.post("/{job_application_id}/{job_ad_id}/request-match")
def request_match(
    job_application_id: UUID,
    job_ad_id: UUID,
    user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JSONResponse:
    def _request_match():
        return job_application_service.request_match(
            job_application_id=job_application_id, job_ad_id=job_ad_id, db=db
        )

    return process_request(
        get_entities_fn=_request_match,
        status_code=status_code.HTTP_201_CREATED,
        not_found_err_msg="Could not process match request",
    )


@router.put("/{job_application_id}/{job_ad_id}/match-response")
def handle_match_response(
    job_application_id: UUID,
    job_ad_id: UUID,
    accept_request: bool = Field(..., description="Accept or Reject Match request"),
    user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JSONResponse:
    def _handle_match_response():
        return job_application_service.handle_match_response(
            job_application_id=job_application_id,
            job_ad_id=job_ad_id,
            accept_request=accept_request,
            db=db,
        )

    return process_request(
        get_entities_fn=_handle_match_response,
        status_code=status_code.HTTP_200_OK,
        not_found_err_msg="Could not accept match request",
    )


@router.get("/{job_application_id}/match-requests", description="View Match requests.")
def view_match_requests(
    job_application_id: UUID,
    user: UserResponse = Depends(),
    db: Session = Depends(),
) -> JSONResponse:
    def _view_match_requests():
        return job_application_service.view_match_requests(
            job_application_id=job_application_id,
            db=db,
        )

    return process_request(
        get_entities_fn=_view_match_requests,
        status_code=status_code.HTTP_200_OK,
        not_found_err_msg="Could not accept match request",
    )
