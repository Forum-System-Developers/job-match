from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.schemas.professional import ProfessionalBase, ProfessionalResponse
from app.services import professional_service
from app.services.auth_service import get_current_user
from app.sql_app.database import get_db
from app.sql_app.professional.professional_status import ProfessionalStatus
from app.sql_app.user.user import User
from app.utils.process_request import process_request

router = APIRouter()


@router.post(
    "/",
    response_model=ProfessionalResponse,
    description="Create a profile for a Professional.",
)
def create(
    professional: ProfessionalBase,
    status: ProfessionalStatus = Form(),
    photo: UploadFile | None = File(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProfessionalResponse:
    """
    Creates a professional profile.

    Args:
        professional (ProfessionalBase): The professional's details from the request body.
        status (ProfessionalStatus): Status of the professional - Active/Busy.
        photo (UploadFile | None): The professional's photo (if provided).
        db (Session): Database session dependency.

    Returns:
        ProfessionalResponse: The created professional profile response.
    """

    def _create():
        return professional_service.create(
            user=user,
            professional=professional,
            status=status,
            db=db,
            photo=photo,
        )

    return process_request(
        get_entities_fn=_create,
        not_found_err_msg="Professional could not be created",
    )


@router.put(
    "/{professional_id}",
    response_model=ProfessionalResponse,
    description="Update a profile for a Professional.",
)
def update(
    professional_id: UUID,
    professional: ProfessionalBase,
    status: ProfessionalStatus = Form(),
    photo: UploadFile | None = File(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProfessionalResponse:
    """
    Update a professional profile.

    Args:
        professional_id (UUID): The identifier of the professional, taken as a path parameter.
        professional (ProfessionalBase): The professional's details from the request body.
        status (ProfessionalStatus): Status of the professional - Active/Busy.
        photo (UploadFile | None): The professional's photo (if provided).
        user (User): The current logged in user.
        db (Session): Database session dependency.

    Returns:
        ProfessionalResponse: The created professional profile response.
    """

    def _update():
        return professional_service.update(
            professional_id=professional_id,
            professional=professional,
            status=status,
            db=db,
            photo=photo,
        )

    return process_request(
        get_entities_fn=_update,
        not_found_err_msg="Professional could not be updated",
    )
