import logging
from uuid import UUID

from fastapi import UploadFile, status
from sqlalchemy.orm import Session, aliased

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.professional import (
    ProfessionalCreate,
    ProfessionalResponse,
)
from app.schemas.common import FilterParams
from app.services import address_service
from app.sql_app.professional.professional import Professional
from app.sql_app.city.city import City
from app.sql_app.professional.professional_status import ProfessionalStatus
from app.sql_app.user.user import User

logger = logging.getLogger(__name__)


def create(
    user: User,
    professional_create: ProfessionalCreate,
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

    if photo is not None:
        upload_photo = photo.file.read()

    professional = Professional(
        **professional_create.model_dump(exclude={"city"}),
        photo=upload_photo,
        user_id=user.id,
        city_id=city.id,
        status=professional_status,
    )

    db.add(professional)
    db.commit()
    db.refresh(professional)

    logger.info(f"Professional with id {professional.id} created")
    return ProfessionalResponse.create(
        professional=professional, city=city.name, application_count=0
    )


def update(
    professional_id: UUID,
    professional_update: ProfessionalCreate,
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

    if professional.city_id != city.id:
        professional.city_id = city.id
        logger.info("professional city updated successfully")

    if professional.description != professional_update.description:
        professional.description = professional_update.description
        logger.info("Professional description updated successfully")

    if professional.status != professional_status:
        professional.status = professional_status
        logger.info("Professional status updated successfully")

    if professional.first_name != professional_update.first_name:
        professional.first_name = professional_update.first_name
        logger.info("Professional first name updated successfully")

    if professional.last_name != professional_update.last_name:
        professional.last_name = professional_update.last_name
        logger.info("Professional last name updated successfully")

    if photo is not None:
        updload_photo = photo.file.read()
        professional.photo = updload_photo
        logger.info("Professional photo updated successfully")

    db.commit()
    db.refresh(professional)

    logger.info(f"Professional with id {professional.id} updated successfully")
    return ProfessionalResponse.create(
        professional=professional,
        city=city.name,
        application_count=professional.active_application_count,
    )


def get_all(db: Session, filter_params: FilterParams) -> list[ProfessionalResponse]:
    """
    Retrieve all Professional profiles.

    Args:
        db (Session): The database session.
        filer_params (FilterParams): Pydantic schema for filtering params.
    Returns:
        list[ProfessionalResponse]: A list of Professional Profiles that are visible for Companies.
    """

    query = (
        db.query(Professional, City.name)
        .join(City, Professional.city_id == City.id)
        .filter(Professional.status == ProfessionalStatus.ACTIVE)
    )

    logger.info("Retreived all professional profiles that are with status ACTIVE")

    query = query.offset(filter_params.offset).limit(filter_params.limit).all()

    logger.info("Limited public topics based on offset and limit")

    return [
        ProfessionalResponse.create(
            professional=professional,
            city=city_name,
            application_count=professional.active_application_count,
        )
        for professional, city_name in query
    ]


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


def get_by_id(professional_id: UUID, db: Session) -> ProfessionalResponse:
    professional = _get_by_id(professional_id=professional_id, db=db)
    if professional is None:
        logger.error(f"Professional with id {professional_id} not found")
        raise ApplicationError(
            detail=f"Professional with id {professional_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    logger.info(f"Professional with id {professional.id} created")
    return ProfessionalResponse.model_validate(professional, from_attributes=True)
