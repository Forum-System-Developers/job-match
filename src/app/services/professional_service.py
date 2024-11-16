import logging
from uuid import UUID

from fastapi import UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.professional import ProfessionalBase, ProfessionalResponse
from app.sql_app.professional.professional import Professional
from app.sql_app.professional.professional_status import ProfessionalStatus
from app.sql_app.user.user import User

logger = logging.getLogger(__name__)


def create(
    user: User,
    professional_create: ProfessionalBase,
    professional_status: ProfessionalStatus,
    db: Session,
    photo: UploadFile | None = None,
) -> ProfessionalResponse:
    """
    Creates an instance of the Professional model.

    Args:
        user (User): Current logged in user.
        professional (str): Pydantic schema for collecting data.
        professional_status (ProfessionalStatus): The status of the Professional.
        db (Session): Database dependency.
        photo (UploadFile | None): Photo of the professional.

    Returns:
        Professional: Professional Pydantic response model.
    """
    # city = cities_service.get_by_name() #TODO

    if photo is not None:
        updload_photo = photo.file.read()

    professional = Professional(
        **professional_create.model_dump(exclude={"city"}),
        photo=updload_photo,
        user_id=user.id,
        # city_id=city.id, #TODO
        status=professional_status,
    )

    db.add(professional)
    db.commit()
    db.refresh(professional)

    logger.info(f"Professional with id {professional.id} created")
    return ProfessionalResponse.model_validate(professional, from_attributes=True)


def update(
    professional_id: UUID,
    professional_update: ProfessionalBase,
    professional_status: ProfessionalStatus,
    db: Session,
    photo: UploadFile | None = None,
) -> ProfessionalResponse:
    """
    Upates an instance of the Professional model.

    Args:
        professional (str): Pydantic schema for collecting data.
        professional_status (ProfessionalStatus): The status of the Professional.
        db (Session): Database dependency.
        photo (UploadFile | None): Photo of the professional.

    Returns:
        Professional: Professional Pydantic response model.
    """
    professional = _get_by_id(professional_id=professional_id, db=db)
    # city = cities_service.get_by_name() #TODO

    if not professional:
        logger.error(f"Professional with id {professional_id} not found")
        raise ApplicationError(
            detail="Professional not found", status_code=status.HTTP_404_NOT_FOUND
        )

    # professional.city_id = city.id # TODO
    professional.description = professional_update.description
    professional.status = professional_status
    professional.first_name = professional_update.first_name
    professional.last_name = professional_update.last_name

    if photo is not None:
        updload_photo = photo.file.read()
        professional.photo = updload_photo

    db.commit()
    db.refresh(professional)

    logger.info(f"Professional with id {professional.id} created")
    return ProfessionalResponse.model_validate(professional, from_attributes=True)


def _get_by_id(professional_id: UUID, db: Session) -> Professional | None:
    """
    Retrieves an instance of the Professional model or None.

    Args:
        professional_id (UUID): The identifier.
        db (Session): Database dependency.

    Returns:
        Professional: SQLAlchemy model for Professional.
    """
    professional = (
        db.query(Professional).filter(Professional.id == professional_id).first()
    )

    return professional
