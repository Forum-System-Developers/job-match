from typing import Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from src.app.schemas.professional import ProfessionalBase, ProfessionalResponse
from src.app.services import professional_service
from src.app.sql_app.database import get_db
from src.app.sql_app.professional.professional_status import ProfessionalStatus
from src.app.utils.process_request import process_request

router = APIRouter()


@router.post(
    "/",
    response_model=ProfessionalResponse,
    description="Create a profile for a Professional.",
)
def create(
    professional: ProfessionalBase,
    status: ProfessionalStatus = Form(),
    photo: Optional[UploadFile] = File(None),
    # user: User = Depends(get_current_user),
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
            # user=user,
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
    "/",
    response_model=ProfessionalResponse,
    description="Update a profile for a Professional.",
)
def update(
    professional: ProfessionalBase,
    status: ProfessionalStatus = Form(),
    photo: UploadFile | None = File(None),
    # user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProfessionalResponse:
    """
    Update a professional profile.

    Args:
        professional (ProfessionalBase): The professional's details from the request body.
        status (ProfessionalStatus): Status of the professional - Active/Busy.
        photo (UploadFile | None): The professional's photo (if provided).
        db (Session): Database session dependency.

    Returns:
        ProfessionalResponse: The created professional profile response.
    """

    def _update():
        return professional_service.update(
            # user=user,
            professional=professional,
            status=status,
            db=db,
            photo=photo,
        )

    return process_request(
        get_entities_fn=_update,
        not_found_err_msg="Professional could not be updated",
    )
