import logging
from uuid import UUID

from fastapi import status
from sqlalchemy.engine import Result, Row
from sqlalchemy.orm import Session

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.common import FilterParams, SearchParams
from app.schemas.job_application import JobAplicationBase, JobApplicationResponse
from app.schemas.job_application import JobStatus as JobStatusInput
from app.schemas.user import UserResponse
from app.services import address_service, professional_service
from app.sql_app.job_ad.job_ad_status import JobAdStatus
from app.sql_app.city.city import City
from app.sql_app.job_application import job_application_status as model_status
from app.sql_app.job_application.job_application import JobApplication
from app.sql_app.job_application.job_application_status import JobStatus
from app.sql_app.professional.professional import Professional

logger = logging.getLogger(__name__)


def create(
    user: UserResponse,
    application: JobAplicationBase,
    is_main: bool,
    application_status: JobStatusInput,
    db: Session,
) -> JobApplicationResponse:
    """
    Creates an instance of the Job Application model.

    Args:
        user (UserResponse): Current logged in user.
        application (ProfessionalBase): Pydantic schema for collecting data.
        is_main (bool): Statement representing is the User wants to set this Application as their Main application.
        application_status (JobStatus): The status of the Job Application - can be ACTIVE, HIDDEN or PRIVATE.
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
    application_status: JobStatusInput,
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
    if job_application.status.value != application_status.value:
        job_application.status = model_status.JobStatus(application_status.value)
        logger.info("Job Application status updated")

    # TODO
    if any(skill not in job_application.skills for skill in application.skills):
        pass

    logger.info(f"Job Application {job_application} updated")

    return JobApplicationResponse.create(
        professional=professional, job_application=job_application, city=city.name
    )


def get_all(
    filter_params: FilterParams,
    db: Session,
    status: JobAdStatus,
    search_params: SearchParams,
):
    """
    Retrieve all Job Applications that match the filtering parameters and keywords.

    Args:
        filer_params (FilterParams): Pydantic schema for filtering params.
        status (JobAdStatus): Can be ACTIVE or ARCHIVED.
        search (str): Search keyword.
        db (Session): The database session.
    Returns:
        list[JobApplicationResponse]: A list of Job Applications that are visible for Companies.
    """
    if status == JobAdStatus.ACTIVE:
        query = _get_for_status(
            filter_params=filter_params, db=db, job_status=JobAdStatus.ACTIVE
        )
    else:
        query = _get_for_status(
            filter_params=filter_params, db=db, job_status=JobStatus.MATCHED
        )

    if search_params.order == "desc":
        query = query.order_by(getattr(JobApplication, search_params.order_by).desc())
    else:
        query = query.order_by(getattr(JobApplication, search_params.order_by).asc())

    logger.info("Order applications based on search params order and order_by")

    result = query.offset(filter_params.offset).limit(filter_params.limit)  # type: ignore

    logger.info("Limited applications based on offset and limit")

    return [
        JobApplicationResponse.create(
            job_application=row[0],
            professional=row[1],
            city=row[2].name,
        )
        for row in result.all()
    ]


def _get_for_status(
    filter_params: FilterParams, db: Session, job_status: JobStatus
) -> Result:
    """
    Retrieve all Job Applications with indicated status.

    Args:
        db (Session): The database session.
        filer_params (FilterParams): Pydantic schema for filtering params.
    Returns:
        A RowReturningQuery object that contains a tuple of JobApplication, Professional and City objects.
    """
    query: Result[tuple[JobApplication, Professional, City]] = (
        db.query(JobApplication, Professional, City)
        .join(Professional, JobApplication.professional_id == Professional.id)
        .join(City, JobApplication.city_id == City.id)
        .filter(JobApplication.status == job_status)  # type: ignore
    )

    logger.info(
        f"Retreived all Job Applications that are with status {job_status.value}"
    )

    return query


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


def _search_by_skills(skills: list, db: Session):
    pass
