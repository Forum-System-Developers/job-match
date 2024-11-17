from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Form, Query
from fastapi import status as status_code
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.schemas.common import FilterParams
from app.schemas.job_application import JobAplicationBase, JobStatus
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
    application: JobAplicationBase,
    is_main: bool = Form(description="Set the Job application as main"),
    application_status: JobStatus = Form(description="Status of the Job Application"),
    user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    Creates a Job Application.

    Args:
        application (JobAplicationBase): The Job Application details from the request body.
        is_main (bool): Statement representing is the User wants to set this Application as their Main application.
        application_status (JobStatus): Status of the Job Application - can be ACTIVE, HIDDEN or PRIVATE.
        user (UserResponse): The current logged in User.
        db (Session): Database session dependency.

    Returns:
        JSONResponse: The created Job Application response.
    """

    def _create():
        return job_application_service.create(
            user=user,
            application=application,
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
    application: JobAplicationBase,
    is_main: bool = Form(description="Set the Job application as main"),
    application_status: JobStatus = Form(description="Status of the Job Application"),
    user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    Updates a Job Application.

    Args:
        job_application_id (UUID): The identifier of the Job Application.
        application (JobAplicationBase): The Job Application details from the request body.
        is_main (bool): Statement representing is the User wants to set this Application as their Main application.
        application_status (JobStatus): Status of the Job Application - can be ACTIVE, HIDDEN or PRIVATE.
        user (UserResponse): The current logged in User.
        db (Session): Database session dependency.

    Returns:
        JSONResponse: The created Job Application response.
    """

    def _update():
        return job_application_service.update(
            job_application_id=job_application_id,
            user=user,
            application=application,
            is_main=is_main,
            application_status=application_status,
            db=db,
        )

    return process_request(
        get_entities_fn=_update,
        status_code=status_code.HTTP_200_OK,
        not_found_err_msg="Job application could not be updated",
    )


@router.get("/active", description="Get all Active Job applications")
def get_active(
    filter_params: Annotated[FilterParams, Query()] = FilterParams(),
    user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    Retrieve all Professional profiles with status Active.

    Args:
        db (Session): The database session.
        filer_params (FilterParams): Pydantic schema for filtering params.
    Returns:
        list[JobApplicationResponse]: A list of Job Applications that are visible for Companies.
    """

    def _get_active():
        return job_application_service.get_active(db=db, filter_params=filter_params)

    return process_request(
        get_entities_fn=_get_active,
        status_code=status_code.HTTP_200_OK,
        not_found_err_msg="Could not fetch Job Applications",
    )
