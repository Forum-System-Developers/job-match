import logging
from uuid import UUID

from fastapi import status
from sqlalchemy.orm import Session
from sqlalchemy.orm.query import Query

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.address import CityResponse
from app.schemas.common import FilterParams, SearchParams
from app.schemas.job_ad import BaseJobAd
from app.schemas.job_application import (
    JobApplicationCreate,
    JobApplicationResponse,
    JobApplicationUpdate,
    JobSearchStatus,
)
from app.schemas.job_application import JobStatus as JobStatusInput
from app.schemas.job_application import MatchResponseRequest
from app.schemas.professional import ProfessionalResponse
from app.schemas.skill import SkillBase
from app.schemas.user import User
from app.services import (
    city_service,
    job_ad_service,
    match_service,
    professional_service,
    skill_service,
)
from app.sql_app.job_application.job_application import JobApplication
from app.sql_app.job_application.job_application_status import JobStatus
from app.sql_app.job_application_skill.job_application_skill import JobApplicationSkill
from app.sql_app.skill.skill import Skill

logger = logging.getLogger(__name__)


def create(
    user: User,
    application_create: JobApplicationCreate,
    is_main: bool,
    application_status: JobStatusInput,
    db: Session,
) -> JobApplicationResponse:
    """
    Creates an instance of the Job Application model.

    Args:
        user (User): Current logged in user.
        application_create (JobApplicationCreate): Pydantic schema for collecting data.
        is_main (bool): Statement representing is the User wants to set this Application as their Main application.
        application_status (JobStatusInput): The status of the Job Application - can be ACTIVE, HIDDEN or PRIVATE.
        db (Session): Database dependency.

    Returns:
        JobApplicationResponse: JobApplication Pydantic response model.
    """
    professional: ProfessionalResponse = professional_service.get_by_id(
        professional_id=user.id, db=db
    )

    city: CityResponse = city_service.get_by_name(
        city_name=application_create.city, db=db
    )

    professional.active_application_count += 1

    job_application: JobApplication = JobApplication(
        **application_create.model_dump(exclude={"city"}),
        is_main=is_main,
        status=JobStatus(application_status.value),
        city_id=city.id,
        professional_id=professional.id,
    )
    logger.info(f"Job Application with id {job_application.id} created")

    db.add(job_application)
    db.commit()
    db.refresh(job_application)

    if application_create.skills:
        _update_skillset(
            db=db,
            job_application_model=job_application,
            skills=set(application_create.skills),
        )
        logger.info(f"Job Application id {job_application.id} skillset created")

    return JobApplicationResponse.create(
        professional=professional, job_application=job_application
    )


def update(
    job_application_id: UUID,
    user: User,
    application_update: JobApplicationUpdate,
    is_main: bool,
    application_status: JobStatusInput,
    db: Session,
) -> JobApplicationResponse:
    """
    Updates an instance of the Job Application model.

    Args:
        job_application_id (UUID): The identifier of the Job Application.
        user (User): Current logged in user.
        application_update (JobApplicationUpdate): Pydantic schema for collecting data.
        is_main (bool): Statement representing is the User wants to set this Application as their Main application.
        application_status (JobStatusInput): The status of the Job Application - can be ACTIVE, HIDDEN or PRIVATE.
        db (Session): Database dependency.

    Returns:
        JobApplicationResponse: JobApplication Pydantic response model.
    """
    job_application: JobApplication = _get_by_id(
        job_application_id=job_application_id, db=db
    )
    professional: ProfessionalResponse = professional_service.get_by_id(
        professional_id=user.id, db=db
    )

    job_application = _update_attributes(
        application_update=application_update,
        job_application_model=job_application,
        is_main=is_main,
        application_status=application_status,
        professional=professional,
        db=db,
    )

    logger.info(f"Job Application with id {job_application.id} updated")

    return JobApplicationResponse.create(
        professional=professional, job_application=job_application
    )


def get_all(
    filter_params: FilterParams,
    db: Session,
    search_params: SearchParams,
) -> list[JobApplicationResponse]:
    """
    Retrieve all Job Applications that match the filtering parameters and keywords.

    Args:
        filer_params (FilterParams): Pydantic schema for filtering params.
        status (JobSearchStatus): Can be ACTIVE or MATCHED.
        search (str): Search keyword.
        db (Session): The database session.
    Returns:
        list[JobApplicationResponse]: A list of Job Applications that are visible for Companies.
    """
    query: Query = db.query(JobApplication).filter(
        JobApplication.status == JobSearchStatus.ACTIVE
    )

    if search_params.skills:
        query.join(JobApplicationSkill).join(Skill).filter(
            Skill.name.in_(search_params.skills)
        )
        logger.info("Filtered applications by skills.")

    if search_params.order == "desc":
        query.order_by(getattr(JobApplication, search_params.order_by).desc())
    else:
        query.order_by(getattr(JobApplication, search_params.order_by).asc())
    logger.info(
        f"Order applications based on search params order {search_params.order} and order_by {search_params.order_by}"
    )

    result: Query = query.offset(filter_params.offset).limit(filter_params.limit)

    logger.info("Limited applications based on offset and limit")

    return [
        JobApplicationResponse.create(
            job_application=row[0],
            professional=row[1],
        )
        for row in result.all()
    ]


def get_by_id(job_application_id: UUID, db: Session) -> JobApplicationResponse:
    """
    Fetches a Job Application by its ID.

    Args:
        job_application_id (UUID): The identifier of the Job application.
        db (Session): Database dependency.

    Returns:
        JobApplicationResponse: JobApplication reponse model.
    """

    job_application: JobApplication = _get_by_id(
        job_application_id=job_application_id, db=db
    )

    return JobApplicationResponse.create(
        professional=job_application.professional, job_application=job_application
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

    job_application: JobApplication | None = (
        db.query(JobApplication).filter(JobApplication.id == job_application_id).first()
    )
    if job_application is None:
        logger.error(f"Job application with id {job_application_id} not found")
        raise ApplicationError(
            detail=f"Job Aplication with id {job_application_id} not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return job_application


def _update_attributes(
    application_update: JobApplicationUpdate,
    job_application_model: JobApplication,
    is_main: bool,
    application_status: JobStatusInput,
    professional: ProfessionalResponse,
    db: Session,
) -> JobApplication:
    """
    Updates the attributes of a Job Application.

    Args:

        application_update (JobAplicationUpdate): Pydantic schema for collecting data.
        job_application_model (JobApplication): The Job Application to be updated.
        is_main (bool): Statement representing is the User wants to set this Application as their Main application.
        application_status (JobStatusInput): The status of the Job Application - can be ACTIVE, HIDDEN or PRIVATE.
        city (CityResponse): The city the professional is located in.

    Returns:
        JobApplication: Updated Job Application ORM model.
    """

    if job_application_model.min_salary != application_update.min_salary:
        job_application_model.min_salary = application_update.min_salary
        logger.info(f"Job Application id {job_application_model.id} min_salary updated")

    if job_application_model.max_salary != application_update.max_salary:
        job_application_model.max_salary = application_update.max_salary
        logger.info(f"Job Application id {job_application_model.id} max_salary updated")

    if job_application_model.description != application_update.description:
        job_application_model.description = application_update.description
        logger.info(
            f"Job Application id {job_application_model.id} description updated"
        )

    if job_application_model.is_main != is_main:
        job_application_model.is_main = is_main
        logger.info(
            f"Job Application id {job_application_model.id} isMain status updated"
        )

    if job_application_model.status.value != application_status.value:
        job_application_model.status = JobStatus(application_status.value)
        logger.info(f"Job Application id {job_application_model.id} status updated")

    if (
        application_update.city is not None
        and application_update.city != job_application_model.city.name
    ):
        city: CityResponse = city_service.get_by_name(
            city_name=application_update.city, db=db
        )

        job_application_model.city_id = city.id
        logger.info(f"Job Application id {job_application_model.id} city updated")

    if any(
        (skill not in job_application_model.skills)
        for skill in application_update.skills
    ):
        new_skills: set[SkillBase] = {
            s
            for s in application_update.skills
            if s.name not in job_application_model.skills
        }
        _update_skillset(
            db=db, job_application_model=job_application_model, skills=new_skills
        )

    return job_application_model


def _update_skillset(
    db: Session,
    job_application_model: JobApplication,
    skills: set[SkillBase],
):
    """
    Updates the skillset for a Job Application.

    Args:

        db (Session): Database dependency.
        job_application_model (JobApplication): The ORM model instance for Job Application.
        skills (list[SkillBase]): List of Pydantic schemas representing each skill in the skillset.

    Returns:
        None
    """

    for skill in skills:
        if not skill_service.exists(db=db, skill_name=skill.name):
            skill_service.create_skill(db=db, skill_schema=skill)

        skill_id = skill_service.get_id(db=db, skill_name=skill.name)
        skill_service.create_job_application_skill(
            db=db, skill_id=skill_id, job_application_id=job_application_model.id
        )

    logger.info(f"Job Application id {job_application_model.id} skillset updated")


def request_match(job_application_id: UUID, job_ad_id: UUID, db: Session) -> dict:
    """
    Verifies Job Application and Job Ad and initiates a Match request for a Job Ad.

    Args:
        job_application_id (UUID): The identifier of the Job Application.
        job_ad_id (UUID): The identifier of the Job Ad.
        db (Session): Database dependency.

    Returns:
        dict: A dictionary containing a success message if the match request is created successfully.

    """
    job_application = _get_by_id(job_application_id=job_application_id, db=db)
    job_ad = job_ad_service.get_by_id(id=job_application_id, db=db)

    return match_service.create_if_not_exists(
        job_application_id=job_application.id, job_ad_id=job_ad.id, db=db
    )


def handle_match_response(
    job_application_id: UUID,
    job_ad_id: UUID,
    accept_request: MatchResponseRequest,
    db: Session,
):
    """
    Verifies Job Application and Job Ad and accepts or rejects a Match request from a Company.

    Args:
        job_application_id (UUID): The identifier of the Job Application.
        job_ad_id (UUID): The identifier of the Job Ad.
        accept_request (MatchResponseRequest): Accept or reject Match request.
        db (Session): Database dependency.

    Returns:
        dict: A dictionary containing a success message if the match request is created successfully.

    """
    job_application = _get_by_id(job_application_id=job_application_id, db=db)
    job_ad = job_ad_service.get_by_id(id=job_ad_id, db=db)

    return match_service.process_request_from_company(
        job_application_id=job_application.id,
        job_ad_id=job_ad.id,
        accept_request=accept_request,
        db=db,
    )


def view_match_requests(
    job_application_id: UUID, db: Session, filter_params: FilterParams
) -> list[BaseJobAd]:
    """
    Verifies Job Application id and fetches all its related Match requests.

    Args:
        job_application_id (UUID): The identifier of the Job Application.
        filter_params (FilterParams): Pagination for the results.
        db (Session): Database dependency.

    Returns:
        list[BaseJobAd]: A list of Pydantic Job Ad response models that correspond to the Job Ads related to the match requests for the given Job Application.

    """
    job_application = _get_by_id(job_application_id=job_application_id, db=db)

    return match_service.get_match_requests_for_job_application(
        job_application_id=job_application.id, filter_params=filter_params, db=db
    )
