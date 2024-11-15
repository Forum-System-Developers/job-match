from typing import Optional

from fastapi import APIRouter, UploadFile, File, Depends, Form
from sqlalchemy.orm import Session

from src.app.schemas.professional import ProfessionalResponse, ProfessionalBase
from src.app.sql_app.database import get_db
from src.app.services import professional_service
from src.app.utils.process_request import process_request

from src.app.sql_app.professional.professional_status import ProfessionalStatus


router = APIRouter()


@router.post(
    "/create",
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
        photo (Optional[UploadFile]): The professional's photo (if provided).
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
        not_found_err_msg=f"Job Ad with id {id} not found",
    )
