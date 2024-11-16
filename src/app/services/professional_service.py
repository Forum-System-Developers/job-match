import logging
from uuid import UUID

from fastapi import UploadFile, status
from sqlalchemy.orm import Session

from src.app.exceptions.custom_exceptions import ApplicationError
from src.app.schemas.professional import (
    ProfessionalBase,
    ProfessionalResponse,
    FilterParams,
)
from src.app.sql_app.professional.professional import Professional
from src.app.sql_app.professional.professional_status import ProfessionalStatus
from src.app.sql_app.user.user import User

logger = logging.getLogger(__name__)


def create(
    user: User,
    professional: ProfessionalBase,
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

    professional = Professional(
        **professional.model_dump(exclude={"city"}),
        photo=photo,
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
    update_professional: ProfessionalBase,
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
    professional.description = update_professional.description
    professional.status = professional_status
    professional.first_name = update_professional.first_name
    professional.last_name = update_professional.last_name

    db.commit()
    db.refresh(professional)

    logger.info(f"Professional with id {professional.id} created")
    return ProfessionalResponse.model_validate(professional, from_attributes=True)


def get_all(db: Session, filter_params: FilterParams) -> list[ProfessionalResponse]:
    """
    Retrieve all Professional profiles.

    Args:
        db (Session): The database session.
        filer_params (FilterParams): Pydantic schema for filtering params.
    Returns:
        list[ProfessionalResponse]: A list of Professional Profiles that are visible for Companies.
    """

    query = db.query(Professional).filter(
        Professional.status == ProfessionalStatus.ACTIVE
    )
    logger.info("Retreived all professional profiles that are with status ACTIVE")

    query = query.offset(filter_params.offset).limit(filter_params.limit).all()
    logger.info("Limited public topics based on offset and limit")

    return query


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
