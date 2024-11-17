from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Form
from fastapi import status as status_code
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.schemas.job_application import JobAplicationBase
from app.services import professional_service
from app.services.auth_service import get_current_user
from app.sql_app.database import get_db
from app.sql_app.user.user import User
from app.utils.process_request import process_request
from app.sql_app.job_application.job_application_status import JobStatus


router = APIRouter()


@router.post(
    "/",
    description="Create a Job Application.",
)
def create(
    application: JobAplicationBase,
    is_main: bool = Form(description="Set the Job application as main"),
    application_status: JobStatus = Form(description="Status of the Job Application"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    Creates a professional profile.

    Args:
        professional (ProfessionalBase): The professional's details from the request body.
        status (ProfessionalStatus): Status of the professional - Active/Busy.
        photo (UploadFile | None): The professional's photo (if provided).
        user (UserResponse): The current logged in User.
        db (Session): Database session dependency.

    Returns:
        JSONResponse: The created professional profile response.
    """

    def _create():
        return professional_service.create(
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
