from typing import Optional

from fastapi import UploadFile
from sqlalchemy.orm import Session

from src.app.sql_app.professional.professional import Professional
from src.app.schemas.professional import ProfessionalBase
from src.app.sql_app.professional.professional_status import ProfessionalStatus

from src.app.utils.logger import get_logger

logger = get_logger(__name__)


def create(
    # user: User,
    professional: ProfessionalBase,
    status: ProfessionalStatus,
    db: Session,
    photo: Optional[UploadFile] = None,
) -> Professional:
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
        professional.model_dump(),
        # user_id=user.id,
        # city_id=city.id,
        status=status,
    )
