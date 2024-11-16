from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi import status as status_code
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.schemas.job_application import JobAplicationBase
from app.services import professional_service
from app.services.auth_service import get_current_user
from app.sql_app.database import get_db
from app.sql_app.user.user import User
from app.utils.process_request import process_request

router = APIRouter()


@router.post(
    "/",
    description="Create a profile for a Professional.",
)
def create(
    application: JobAplicationBase,
    is_main: bool = Form(default=True, description="Default send value is True"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    Creates a professional profile.

    Args:
        professional (ProfessionalBase): The professional's details from the request body.
        status (ProfessionalStatus): Status of the professional - Active/Busy.
        photo (UploadFile | None): The professional's photo (if provided).
        user (User): The current logged in User.
        db (Session): Database session dependency.

    Returns:
        ProfessionalResponse | JSONResponse: The created professional profile response.
    """

    def _create():
        return professional_service.create(
            user=user, application=application, is_main=is_main, db=db
        )

    return process_request(
        get_entities_fn=_create,
        status_code=status_code.HTTP_201_CREATED,
        not_found_err_msg="Job application could not be created",
    )
