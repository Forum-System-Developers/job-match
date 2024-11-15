import logging
from uuid import UUID
from typing import Optional

from fastapi import UploadFile, status
from sqlalchemy.orm import Session

from src.app.schemas.professional import ProfessionalBase, ProfessionalResponse
from src.app.exceptions.custom_exceptions import ApplicationError
from src.app.sql_app.professional.professional import Professional
from src.app.sql_app.professional.professional_status import ProfessionalStatus

logger = logging.getLogger(__name__)


def create(
    # user: User, # TODO
    professional: ProfessionalBase,
    professional_status: ProfessionalStatus,
    db: Session,
    photo: Optional[UploadFile] = None,
) -> ProfessionalResponse:
    """
    Creates an instance of the Professional model.

    Args:
        first_name (str): First name of the professional.
        last_name (str): Last name of the professional.
        description (str): Description of the professional.
        photo Optional[bytes]: Photo of the professional.
        db (Session): Database dependency.

    Returns:
        Professional: Professional Pydantic response model.
    """
    # city = cities_service.get_by_name() #TODO

    professional = Professional(
        **professional.model_dump(exclude={"city"}),
        photo=photo,
        # user_id=user.id, #TODO
        # city_id=city.id, #TODO
        status=professional_status,
    )

    db.add(professional)
    db.commit()
    db.refresh(professional)

    logger.info(f"Professional with id {professional.id} created")
    return ProfessionalResponse.model_validate(professional, from_attributes=True)


def update(
    # user: User, # TODO
    update_professional: ProfessionalBase,
    professional_status: ProfessionalStatus,
    db: Session,
    photo: UploadFile | None = None,
) -> ProfessionalResponse:
    """
    Upates an instance of the Professional model.

    Args:
        first_name (str): First name of the professional.
        last_name (str): Last name of the professional.
        description (str): Description of the professional.
        photo Optional[bytes]: Photo of the professional.
        db (Session): Database dependency.

    Returns:
        Professional: Professional Pydantic response model.
    """
    professional = _get_by_id(professional_id=None, db=db)  # TODO
    # city = cities_service.get_by_name() #TODO

    # if not professional: #TODO
    #     logger.error(f"Professional with id {user.id} not found")
    #     raise ApplicationError(
    #         detail="Professional not found",
    #         status_code=status.HTTP_404_NOT_FOUND
    #     )
    # if professional.city_id != city.id:
    #     professional.city_id = city.id # TODO

    professional.description = update_professional.description
    professional.status = professional_status
    professional.first_name = update_professional.first_name
    professional.last_name = update_professional.last_name

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
