import logging
from uuid import UUID

from fastapi import UploadFile, status
from sqlalchemy import Row
from sqlalchemy.orm import Session

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.common import FilterParams
from app.schemas.professional import ProfessionalCreate, ProfessionalResponse
from app.schemas.user import UserResponse
from app.services import address_service
from app.sql_app.city.city import City
from app.sql_app.professional.professional import Professional
from app.sql_app.professional.professional_status import ProfessionalStatus

logger = logging.getLogger(__name__)


def create_skill(db: Session):
    pass
