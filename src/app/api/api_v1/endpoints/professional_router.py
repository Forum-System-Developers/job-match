from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from fastapi import status as status_code
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.schemas.professional import FilterParams, ProfessionalBase
from app.services import professional_service
from app.services.auth_service import get_current_user
from app.sql_app.database import get_db
from app.sql_app.professional.professional_status import ProfessionalStatus
from app.sql_app.user.user import User
from app.utils.process_request import process_request

router = APIRouter()


@router.post(
    "/",
    description="Create a profile for a Professional.",
)
def create(
    professional: ProfessionalBase,
    professional_status: ProfessionalStatus = Form(),
    photo: UploadFile | None = File(None),
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
            user=user,
            professional=professional,
            professional_status=professional_status,
            db=db,
            photo=photo,
        )

    return process_request(
        get_entities_fn=_create,
        status_code=status_code.HTTP_201_CREATED,
        not_found_err_msg="Professional could not be created",
    )


@router.put(
    "/{professional_id}",
    description="Update a profile for a Professional.",
)
def update(
    professional_id: UUID,
    professional: ProfessionalBase,
    professional_status: ProfessionalStatus = Form(),
    photo: UploadFile | None = File(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JSONResponse:
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
            professional_status=professional_status,
            db=db,
            photo=photo,
        )

    return process_request(
        get_entities_fn=_update,
        status_code=status_code.HTTP_200_OK,
        not_found_err_msg="Professional could not be updated",
    )


@router.get(
    "/",
    description="Retreive all Professional profiles.",
)
def get_all(
    filter_params: Annotated[FilterParams, Query()] = FilterParams(),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    Retrieve all Professional profiles with status ACTIVE.

    Args:
        filer_params (FilterParams): Pydantic schema for filtering params.
        user (User): The current logged in User.
        db (Session): The database session.
    Returns:
        list[ProfessionalResponse]: A list of Professional Profiles that are visible for Companies.
    """

    def _get_all():
        return professional_service.get_all(db=db, filter_params=filter_params)

    return process_request(
        get_entities_fn=_get_all,
        status_code=status_code.HTTP_200_OK,
        not_found_err_msg="Could not fetch Professionals",
    )


@router.get(
    "/{professional_id}",
    description="Retreive a Professional profile by its ID.",
)
def get_by_id(
    professional_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    Retrieve all Professional profiles with status ACTIVE.

    Args:
        user (User): The current logged in User.
        db (Session): The database session.
    Returns:
        ProfessionalResponse: A Professional Profile that matches the given ID.
    """

    def _get_by_id():
        return professional_service.get_by_id(professional_id=professional_id, db=db)

    return process_request(
        get_entities_fn=_get_by_id,
        status_code=status_code.HTTP_200_OK,
        not_found_err_msg="Could not fetch Professional",
    )
