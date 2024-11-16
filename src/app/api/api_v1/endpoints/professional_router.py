from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.schemas.professional import (
    ProfessionalBase,
    ProfessionalResponse,
    FilterParams,
)
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
    professional_status: ProfessionalStatus = Form(),
    photo: UploadFile | None = File(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProfessionalResponse | JSONResponse:
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
            user=user,
            professional=professional,
            professional_status=professional_status,
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
    professional_status: ProfessionalStatus = Form(),
    photo: UploadFile | None = File(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProfessionalResponse | JSONResponse:
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
        ProfessionalResponse | JSONResponse: The created professional profile response.
    """

    def _update():
        return professional_service.update(
            professional_id=professional_id,
            professional=professional,
            professional_status=professional_status,
            db=db,
            photo=photo,
        )

    return process_request(
        get_entities_fn=_update,
        not_found_err_msg="Professional could not be updated",
    )


@router.get(
    "/",
    response_model=list[ProfessionalResponse],
    description="Retreive all Professional profiles.",
)
def get_all(
    filter_params: Annotated[FilterParams, Query] = FilterParams(),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ProfessionalResponse] | JSONResponse:
    """
    Retrieve all Professional profiles with status ACTIVE.

    Args:
        filer_params (FilterParams): Pydantic schema for filtering params.
        user (User): The current logged in User.
        db (Session): The database session.
    Returns:
        list[ProfessionalResponse] | JSONResponse: A list of Professional Profiles that are visible for Companies.
    """

    def _get_all():
        return professional_service.get_all()

    return process_request(
        get_entities_fn=_get_all, not_found_err_msg="Could not fetch Professionals"
    )
