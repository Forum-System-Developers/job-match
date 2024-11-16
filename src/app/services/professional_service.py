import logging
from uuid import UUID

from fastapi import UploadFile, status
from sqlalchemy.orm import Session

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.professional import ProfessionalBase, ProfessionalResponse
from app.sql_app.professional.professional import Professional
from app.sql_app.professional.professional_status import ProfessionalStatus
from app.services import address_service
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
        professional_create (ProfessionalBase): Pydantic schema for collecting data.
        professional_status (ProfessionalStatus): The status of the Professional.
        db (Session): Database dependency.
        photo (UploadFile | None): Photo of the professional.

    Returns:
        Professional: Professional Pydantic response model.
    """
    city = address_service.get_by_name(name=professional_create.city, db=db)
    if city is None:
        logger.error(f"City name {professional_create.city} not found")
        raise ApplicationError(
            detail=f"City with name {professional_create.city} was not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    logger.info(f"City {city} fetched")

    professional = Professional(
        **professional_create.model_dump(exclude={"city"}),
        photo=photo,
        user_id=user.id,
        city_id=city.id,
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
        professional_id (UUID): The identifier of the professional.
        professional_update (ProfessionalBase): Pydantic schema for collecting data.
        professional_status (ProfessionalStatus): The status of the Professional.
        db (Session): Database dependency.
        photo (UploadFile | None): Photo of the professional.

    Returns:
        Professional: Professional Pydantic response model.
    """
    professional = _get_by_id(professional_id=professional_id, db=db)
    if professional is None:
        logger.error(f"Professional with id {professional_id} not found")
        raise ApplicationError(
            detail=f"Professional with ID {professional_id} was not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    logger.info(f"Professional with ID {professional_id} fetched")

    city = address_service.get_by_name(name=professional_update.city, db=db)
    if city is None:
        logger.error(f"City name {professional_update.city} not found")
        raise ApplicationError(
            detail=f"City with name {professional_update.city} was not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    logger.info(f"City {city} fetched")

    if not professional:
        logger.error(f"Professional with id {professional_id} not found")
        raise ApplicationError(
            detail="Professional not found", status_code=status.HTTP_404_NOT_FOUND
        )

    professional.city_id = city.id
    professional.description = professional_update.description
    professional.status = professional_status
    professional.first_name = professional_update.first_name
    professional.last_name = professional_update.last_name

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
    return db.query(Professional).filter(Professional.id == professional_id).first()
