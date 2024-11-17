from uuid import UUID
import logging

from sqlalchemy.orm import Session

from app.schemas.job_application import JobAplicationBase, JobApplicationResponse
from app.schemas.user import UserResponse
from app.services import address_service, professional_service
from app.sql_app.job_application.job_application import JobApplication
from app.sql_app.job_application.job_application_status import JobStatus

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
    city = address_service.get_by_name(name=application.city, db=db)
    professional = professional_service.get_by_id(professional_id=user.id, db=db)
    job_application = JobApplication(
        **application.model_dump(exclude={"city"}),
        is_main=is_main,
        status=application_status,
        city_id=city.id,
        professional_id=user.id,
    )

    logger.info(f"Job Application {job_application} created")

    return JobApplicationResponse.create(
        professional=professional, job_application=job_application, city=city.name
    )
