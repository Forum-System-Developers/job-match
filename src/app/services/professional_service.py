from typing import Optional

from fastapi import UploadFile
from sqlalchemy.orm import Session

from src.app.schemas.professional import ProfessionalBase, ProfessionalResponse
from src.app.sql_app.professional.professional import Professional
from src.app.sql_app.professional.professional_status import ProfessionalStatus


def create(
    # user: User,
    professional: ProfessionalBase,
    status: ProfessionalStatus,
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
    # city = cities_service.get_by_id()

    professional = Professional(
        **professional.model_dump(),
        photo=photo,
        # user_id=user.id,
        # city_id=city.id,
        status=status,
    )

    db.add(professional)
    db.commit()
    db.refresh(professional)

    return ProfessionalResponse.model_validate(professional, from_attributes=True)
