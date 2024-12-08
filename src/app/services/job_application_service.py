import logging
from uuid import UUID

from fastapi import status
from sqlalchemy.orm import Session

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.city import CityResponse
from app.schemas.common import FilterParams, SearchParams
from app.schemas.job_application import (
    JobApplicationCreate,
    JobApplicationCreateFinal,
    JobApplicationResponse,
    JobApplicationUpdate,
    JobApplicationUpdateFinal,
    MatchResponseRequest,
)
from app.schemas.match import MatchRequestAd
from app.schemas.skill import SkillBase, SkillResponse
from app.services import city_service, job_ad_service, match_service, skill_service
from app.services.enums.job_application_status import JobStatus
from app.services.utils.validators import (
    ensure_valid_city,
    ensure_valid_job_application_id,
    ensure_valid_professional_id,
)
from app.sql_app.job_application.job_application import JobApplication
from app.sql_app.professional.professional import Professional
from app.utils.processors import process_db_transaction
from app.utils.request_handlers import (
    perform_get_request,
    perform_post_request,
    perform_put_request,
)
from tests.services.urls import (
    JOB_APPLICATIONS_ALL_URL,
    JOB_APPLICATIONS_BY_ID_URL,
    JOB_APPLICATIONS_URL,
)

logger = logging.getLogger(__name__)


def get_all(
    filter_params: FilterParams,
    search_params: SearchParams,
) -> list[JobApplicationResponse]:
    job_applications = perform_post_request(
        url=JOB_APPLICATIONS_ALL_URL,
        json=search_params.model_dump(mode="json"),
        params=filter_params.model_dump(),
    )
    logger.info(f"Retrieved {len(job_applications)} job applications")

    return [
        JobApplicationResponse(**job_application)
        for job_application in job_applications
    ]


def create(
    professional_id: UUID,
    job_application_data: JobApplicationCreate,
) -> JobApplicationResponse:
    """
    Creates a new job application.

    Args:
        professional_id (UUID): The unique identifier of the professional.
        job_application_data (JobApplicationCreate): The data required to create a job application.

    Returns:
        JobApplicationResponse: The response containing the details of the created job application.
    """
    city = city_service.get_by_name(city_name=job_application_data.city)
    job_application_final_data = JobApplicationCreateFinal.create(
        job_application_create=job_application_data,
        city_id=city.id,
        professional_id=professional_id,
    )
    job_application = perform_post_request(
        url=JOB_APPLICATIONS_URL,
        json=job_application_final_data.model_dump(mode="json"),
    )

    return JobApplicationResponse(**job_application)


def update(
    job_application_id: UUID,
    job_application_update: JobApplicationUpdate,
    professional_id: UUID,
) -> JobApplicationResponse:
    """
    Update a job application with the given ID using the provided update data.

    Args:
        job_application_id (UUID): The unique identifier of the job application to be updated.
        job_application_update (JobApplicationUpdate): The data to update the job application with.
        professional_id (UUID): The unique identifier of the professional associated with the job application.

    Returns:
        JobApplicationResponse: The response containing the updated job application data.
    """
    ensure_valid_job_application_id(
        job_application_id=job_application_id,
        professional_id=professional_id,
    )
    job_application_final_data = _prepare_job_application_update_final_data(
        job_application_update=job_application_update
    )

    job_application = perform_put_request(
        url=JOB_APPLICATIONS_BY_ID_URL.format(job_application_id=job_application_id),
        json=job_application_final_data.model_dump(mode="json"),
    )
    logger.info(f"Job application with id {job_application_id} updated")

    return JobApplicationResponse(**job_application)


def get_by_id(job_application_id: UUID) -> JobApplicationResponse:
    """
    Fetches a Job Application by its ID.

    Args:
        job_application_id (UUID): The identifier of the Job application.

    Returns:
        JobApplicationResponse: JobApplication reponse model.
    """
    job_application = perform_get_request(
        url=JOB_APPLICATIONS_BY_ID_URL.format(job_application_id=job_application_id)
    )

    return JobApplicationResponse(**job_application)


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


# def _update_skillset(
#     db: Session,
#     job_application_model: JobApplication,
#     skills: list[SkillBase],
# ) -> None:
#     """
#     Updates the skillset for a Job Application.

#     Args:

#         db (Session): Database dependency.
#         job_application_model (JobApplication): The ORM model instance for Job Application.
#         skills (list[SkillBase]): Set of Pydantic schemas representing each skill in the skillset.

#     Returns:
#         None:
#     """

#     def _handle_update():
#         skills_ids = {skill.skill_id for skill in job_application_model.skills}
#         for skill in skills:
#             if not skill_service.exists(db=db, skill_name=skill.name):
#                 skill_id = skill_service.create_skill(db=db, skill_data=skill)
#             else:
#                 skill_id = skill_service.get_id(skill_name=skill.name, db=db)

#             if skill_id not in skills_ids:
#                 skill_service.create_job_application_skill(
#                     db=db,
#                     skill_id=skill_id,
#                     job_application_id=job_application_model.id,
#                 )

#         db.flush()
#         logger.info(f"Job Application id {job_application_model.id} skillset updated")

#     return process_db_transaction(transaction_func=_handle_update, db=db)


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
    job_ad = job_ad_service.get_by_id(job_ad_id=job_ad_id)

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
    job_ad = job_ad_service.get_by_id(job_ad_id=job_ad_id)

    return match_service.process_request_from_company(
        job_application_id=job_application.id,
        job_ad_id=job_ad.id,
        accept_request=accept_request,
        db=db,
    )


def view_match_requests(
    job_application_id: UUID, db: Session, filter_params: FilterParams
) -> list[MatchRequestAd]:
    """
    Verifies Job Application id and fetches all its related Match requests.

    Args:
        job_application_id (UUID): The identifier of the Job Application.
        filter_params (FilterParams): Pagination for the results.
        db (Session): Database dependency.

    Returns:
        list[MatchRequestAd]: A list of Pydantic response models that correspond to the Job Ads related to the match requests for the given Job Application.

    """
    job_application = _get_by_id(job_application_id=job_application_id, db=db)

    return match_service.get_match_requests_for_job_application(
        job_application_id=job_application.id, filter_params=filter_params, db=db
    )


def _prepare_job_application_update_final_data(
    job_application_update: JobApplicationUpdate,
) -> JobApplicationUpdateFinal:
    job_application_final_data = JobApplicationUpdateFinal.create(
        job_application_update=job_application_update
    )
    if job_application_update.city is not None:
        city = ensure_valid_city(name=job_application_update.city)
        job_application_final_data.city_id = city.id

    return job_application_final_data
