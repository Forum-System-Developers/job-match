import logging
from uuid import UUID

from fastapi import status
from sqlalchemy.orm import Session

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.job_application import JobAplicationBase, JobApplicationResponse
from app.schemas.user import UserResponse
from app.services import address_service, professional_service
from app.sql_app.job_application import job_application_status as model_status
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
        application_status (JobStatus): The status of the Job Application - can be ACTIVE, HIDDEN or PRIVATE.
        db (Session): Database dependency.

    Returns:
        JobApplicationResponse: JobApplication Pydantic response model.
    """
    if application.city is not None:
        city = address_service.get_by_name(name=application.city, db=db)

    professional = professional_service.get_by_id(professional_id=user.id, db=db)
    job_application = JobApplication(
        **application.model_dump(exclude={"city"}),
        is_main=is_main,
        status=model_status.JobStatus(application_status.value),
        city_id=city.id,
        professional_id=user.id,
    )

    logger.info(f"Job Application {job_application} created")

    return JobApplicationResponse.create(
        professional=professional, job_application=job_application, city=city.name
    )


def update(
    job_application_id: UUID,
    user: UserResponse,
    application: JobAplicationBase,
    is_main: bool,
    application_status: JobStatus,
    db: Session,
) -> JobApplicationResponse:
    """
    Updates an instance of the Job Application model.

    Args:
        job_application_id (UUID): The identifier of the Job Application.
        user (UserResponse): Current logged in user.
        application (ProfessionalBase): Pydantic schema for collecting data.
        is_main (bool): Statement representing is the User wants to set this Application as their Main application.
        application_status (JobStatus): The status of the Job Application - can be ACTIVE, HIDDEN or PRIVATE.
        db (Session): Database dependency.

    Returns:
        JobApplicationResponse: JobApplication Pydantic response model.
    """
    job_application = _get_by_id(job_application_id=job_application_id, db=db)

    if application.city is not None:
        city = address_service.get_by_name(name=application.city, db=db)
    if city.id != job_application.city_id:
        job_application.city_id = city.id
        logger.info("Job Application city updated")

    professional = professional_service.get_by_id(professional_id=user.id, db=db)

    if job_application.min_salary != application.min_salary:
        job_application.min_salary = application.min_salary
        logger.info("Job Application min_salary updated")
    if job_application.max_salary != application.max_salary:
        job_application.max_salary = application.max_salary
        logger.info("Job Application max_salary updated")
    if job_application.description != application.description:
        job_application.description = application.description
        logger.info("Job Application description updated")
    if job_application.is_main != is_main:
        job_application.is_main = is_main
        logger.info("Job Application isMain status updated")
    if job_application.status != application_status:
        job_application.status = application_status.value
        logger.info("Job Application status updated")

    if any(skill not in job_application.skills for skill in application.skills):
        pass  # TODO

    logger.info(f"Job Application {job_application} updated")

    return JobApplicationResponse.create(
        professional=professional, job_application=job_application, city=city.name
    )


def _get_by_id(job_application_id: UUID, db: Session) -> JobApplication:
    """
    Fetches a Job Application by its ID.

    Args:
        job_application_id (UUID): The identifier of the Job application.
        db (Session): Database dependency.

    Returns:
        JobApplication: JobApplication ORM model.

    Raises:
        ApplicationError: If a Job Application with this ID does not exist.
    """

    job_application = (
        db.query(JobApplication).filter(JobApplication.id == job_application_id).first()
    )

    if job_application is None:
        raise ApplicationError(
            detail=f"Job Aplication with id {job_application_id} not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return job_application
