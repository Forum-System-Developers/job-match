import logging
from uuid import UUID

from fastapi import status
from sqlalchemy.orm import Session

from app.exceptions.custom_exceptions import ApplicationError
from app.sql_app.professional.professional import Professional
from app.sql_app.job_application.job_application import JobApplication
from app.sql_app.job_application.job_application_status import JobStatus
from app.schemas.job_application import JobAplicationBase, JobApplicationResponse
from app.services import professional_service
from app.schemas.user import UserResponse

logger = logging.getLogger(__name__)


def create(
    user: UserResponse,
    application: JobAplicationBase,
    is_main: bool,
    application_status: JobStatus,
    db: Session,
) -> JobApplicationResponse:
    """
    Creates an instance of the Job Application model.

    Args:
        user (UserResponse): Current logged in user.
        application (ProfessionalBase): Pydantic schema for collecting data.
        is_main (bool): Statement representing is the User wants to set this Application as their Main application.
        application_status (JobStatus): The status of the Job Application - can be ACTIVE, HIDDEN, PRIVATE or MATCHED.
        db (Session): Database dependency.

    Returns:
        JobApplicationResponse: JobApplication Pydantic response model.
    """
    professional = professional_service.get_by_id(professional_id=user.id, db=db)
