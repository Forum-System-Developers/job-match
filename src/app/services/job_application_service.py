import logging
from uuid import UUID

from fastapi import status
from sqlalchemy.orm import Session
from sqlalchemy.orm.query import Query

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.city import CityResponse
from app.schemas.common import FilterParams, SearchParams
from app.schemas.job_ad import JobAdPreview
from app.schemas.job_application import (
    JobApplicationCreate,
    JobApplicationResponse,
    JobApplicationUpdate,
    MatchResponseRequest,
)
from app.schemas.professional import ProfessionalResponse
from app.schemas.skill import SkillBase, SkillResponse
from app.services import city_service, job_ad_service, match_service, skill_service
from app.services.utils.validators import ensure_valid_professional_id
from app.sql_app.job_application.job_application import JobApplication
from app.sql_app.job_application.job_application_status import JobStatus
from app.sql_app.job_application_skill.job_application_skill import JobApplicationSkill
from app.sql_app.professional.professional import Professional
from app.sql_app.skill.skill import Skill
from app.utils.processors import process_db_transaction

logger = logging.getLogger(__name__)


def create(
    professional_id: UUID,
    application_create: JobApplicationCreate,
    db: Session,
) -> JobApplicationResponse:
    """
    Creates an instance of the Job Application model.

    Args:
        professional (ProfessionalResponse): Current logged in Professional.
        application_create (JobApplicationCreate): Pydantic schema for collecting data.
        db (Session): Database dependency.

    Returns:
        JobApplicationResponse: JobApplication Pydantic response model.
    """
    professional: Professional = ensure_valid_professional_id(
        professional_id=professional_id, db=db
    )

    city: CityResponse = city_service.get_by_name(
        city_name=application_create.city, db=db
    )

    job_application = _create(
        professional=professional,
        application_create=application_create,
        city_id=city.id,
        db=db,
    )

    if application_create.skills:
        skills = _create_skillset(
            db=db,
            job_application_model=job_application,
            skills=application_create.skills,
        )
        logger.info(f"Job Application id {job_application.id} skillset created")

    return JobApplicationResponse.create(
        professional=professional,
        job_application=job_application,
        skills=skills if skills else [],
        db=db,
    )


def update(
    job_application_id: UUID,
    professional_id: UUID,
    application_update: JobApplicationUpdate,
    db: Session,
) -> JobApplicationResponse:
    """
    Updates an instance of the Job Application model.

    Args:
        job_application_id (UUID): The identifier of the Job Application.
        application_update (JobApplicationUpdate): Pydantic schema for collecting data.
        db (Session): Database dependency.

    Returns:
        JobApplicationResponse: JobApplication Pydantic response model.
    """
    job_application: JobApplication = _get_by_id(
        job_application_id=job_application_id, db=db
    )
    professional = ensure_valid_professional_id(professional_id=professional_id, db=db)

    job_application = _update_attributes(
        application_update=application_update,
        job_application_model=job_application,
        db=db,
    )

    logger.info(f"Job Application with id {job_application.id} updated")

    return JobApplicationResponse.create(
        professional=professional,
        job_application=job_application,
        db=db,
    )


def get_all(
    filter_params: FilterParams,
    search_params: SearchParams,
    db: Session,
) -> list[JobApplicationResponse]:
    """
    Retrieve all Job Applications that match the filtering parameters and keywords.

    Args:
        filer_params (FilterParams): Pydantic schema for filtering params.
        search_params (SearchParams): Pydantic for search parameteres.
        db (Session): The database session.
    Returns:
        list[JobApplicationResponse]: A list of Job Applications that are visible for Companies.
    """
    query: Query = (
        db.query(JobApplication, Professional)
        .join(Professional, JobApplication.professional_id == Professional.id)
        .filter(
            JobApplication.status == JobStatus.ACTIVE,
        )
    )

    # TODO
    # if search_params.skills:
    #     query = (
    #         query.join(JobApplicationSkill)
    #         .join(Skill)
    #         .filter(Skill.name.in_(search_params.skills))
    #     )
    #     logger.info("Filtered applications by skills.")

    if search_params.order == "desc":
        query.order_by(getattr(JobApplication, search_params.order_by).desc())
    else:
        query.order_by(getattr(JobApplication, search_params.order_by).asc())
    logger.info(
        f"Order applications based on search params order {search_params.order} and order_by {search_params.order_by}"
    )

    result = query.offset(filter_params.offset).limit(filter_params.limit).all()

    logger.info("Limited applications based on offset and limit")

    return [
        JobApplicationResponse.create(
            job_application=row[0], professional=row[1], db=db
        )
        for row in result
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
        professional=job_application.professional,
        job_application=job_application,
        db=db,
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
    db: Session,
) -> JobApplication:
    """
    Updates the attributes of a Job Application.

    Args:

        application_update (JobAplicationUpdate): Pydantic schema for collecting data.
        job_application_model (JobApplication): The Job Application to be updated.
        city (CityResponse): The city the professional is located in.

    Returns:
        JobApplication: Updated Job Application ORM model.
    """
    is_main = application_update.is_main
    application_status = application_update.application_status

    if (
        job_application_model.min_salary is not None
    ) and job_application_model.min_salary != application_update.min_salary:
        job_application_model.min_salary = application_update.min_salary
        logger.info(f"Job Application id {job_application_model.id} min_salary updated")

    if (
        job_application_model.max_salary is not None
    ) and job_application_model.max_salary != application_update.max_salary:
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
    ) and application_update.city != job_application_model.city.name:
        city: CityResponse = city_service.get_by_name(
            city_name=application_update.city, db=db
        )

        job_application_model.city_id = city.id
        logger.info(f"Job Application id {job_application_model.id} city updated")

    if application_update.skills is not None:
        _update_skillset(
            db=db,
            job_application_model=job_application_model,
            skills=application_update.skills,
        )

    def _handle_update():
        db.commit()
        db.refresh(job_application_model)
        logger.info(
            f"Job application with id {job_application_model.id} updated successfully."
        )

        return job_application_model

    return process_db_transaction(transaction_func=_handle_update, db=db)


def _update_skillset(
    db: Session,
    job_application_model: JobApplication,
    skills: list[SkillBase],
) -> None:
    """
    Updates the skillset for a Job Application.

    Args:

        db (Session): Database dependency.
        job_application_model (JobApplication): The ORM model instance for Job Application.
        skills (list[SkillBase]): Set of Pydantic schemas representing each skill in the skillset.

    Returns:
        None:
    """

    def _handle_update():
        skills_ids = {skill.skill_id for skill in job_application_model.skills}
        for skill in skills:
            if not skill_service.exists(db=db, skill_name=skill.name):
                skill_id = skill_service.create_skill(db=db, skill_schema=skill)
            else:
                skill_id = skill_service.get_id(skill_name=skill.name, db=db)

            if skill_id not in skills_ids:
                skill_service.create_job_application_skill(
                    db=db,
                    skill_id=skill_id,
                    job_application_id=job_application_model.id,
                )

        db.flush()
        logger.info(f"Job Application id {job_application_model.id} skillset updated")

    return process_db_transaction(transaction_func=_handle_update, db=db)


def _create_skillset(
    db: Session,
    job_application_model: JobApplication,
    skills: list[SkillBase],
) -> list[SkillResponse]:
    """
    Creates the skillset for a Job Application.

    Args:

        db (Session): Database dependency.
        job_application_model (JobApplication): The ORM model instance for Job Application.
        skills (list[SkillBase]): Set of Pydantic schemas representing each skill in the skillset.

    Returns:
        list[SkillBase]: List of Pydantic schemas representing each skill in the newly created skillset.
    """
    skillset = []

    def _handle_create():
        for skill in skills:
            if not skill_service.exists(db=db, skill_name=skill.name):
                skill_id = skill_service.create_skill(db=db, skill_schema=skill)
            else:
                skill_id = skill_service.get_id(skill_name=skill.name, db=db)

            skill_service.create_job_application_skill(
                db=db,
                skill_id=skill_id,
                job_application_id=job_application_model.id,
            )
            skill = skill_service.get_by_id(skill_id=skill_id, db=db)
            skillset.append(skill)

        db.flush()
        logger.info(f"Job Application id {job_application_model.id} skillset updated")

        return skillset

    return process_db_transaction(transaction_func=_handle_create, db=db)


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
    job_ad = job_ad_service.get_by_id(id=job_ad_id, db=db)

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
) -> list[JobAdPreview]:
    """
    Verifies Job Application id and fetches all its related Match requests.

    Args:
        job_application_id (UUID): The identifier of the Job Application.
        filter_params (FilterParams): Pagination for the results.
        db (Session): Database dependency.

    Returns:
        list[JobAdPreview]: A list of Pydantic Job Ad response models that correspond to the Job Ads related to the match requests for the given Job Application.

    """
    job_application = _get_by_id(job_application_id=job_application_id, db=db)

    return match_service.get_match_requests_for_job_application(
        job_application_id=job_application.id, filter_params=filter_params, db=db
    )


def _create(
    professional: Professional,
    application_create: JobApplicationCreate,
    city_id: UUID,
    db: Session,
) -> JobApplication:
    """
    Creates an instance of the Job Application model.

    Args:
        professional (Professional): Professional associated with the Job Application.
        application_create (JobApplicationCreate): DTO for data collection.
        city_id (UUID): Identifier for the city the Application is associated with.
        db (Session): Database dependency.

    Returns:
        JobApplication: The new instance of the Job Aplication model.
    """

    def _handle_create() -> JobApplication:
        professional.active_application_count += 1

        job_application: JobApplication = JobApplication(
            **application_create.model_dump(exclude={"city", "skills", "status"}),
            city_id=city_id,
            status=JobStatus(application_create.status.value),
            professional_id=professional.id,
        )
        logger.info(f"Job Application with id {job_application.id} created")

        db.add(job_application)
        db.commit()
        db.refresh(job_application)

        return job_application

    return process_db_transaction(transaction_func=_handle_create, db=db)


def get_skills(job_application: JobApplication, db: Session) -> list[SkillResponse]:
    skills_ids = [s.skill_id for s in job_application.skills]
    skills = []
    for skill_id in skills_ids:
        skill = skill_service.get_by_id(skill_id=skill_id, db=db)
        skills.append(skill)

    return skills
