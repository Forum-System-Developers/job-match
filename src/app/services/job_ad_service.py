import logging
from uuid import UUID

from app.schemas.common import FilterParams, JobAdSearchParams, MessageResponse
from app.schemas.job_ad import JobAdCreate, JobAdCreateFull, JobAdResponse, JobAdUpdate
from app.services.external_db_service_urls import (
    JOB_AD_ADD_SKILL_URL,
    JOB_AD_BY_ID_URL,
    JOB_ADS_URL,
)
from app.services.utils.validators import ensure_valid_city, ensure_valid_job_ad_id
from app.utils.request_handlers import (
    perform_get_request,
    perform_post_request,
    perform_put_request,
)

logger = logging.getLogger(__name__)


def get_all(
    filter_params: FilterParams,
    search_params: JobAdSearchParams,
) -> list[JobAdResponse]:
    """
    Retrieve all job advertisements based on filter and search parameters.

    Args:
        filter_params (FilterParams): The parameters to filter the job advertisements.
        search_params (JobAdSearchParams): The parameters to search the job advertisements.

    Returns:
        list[JobAdResponse]: The list of job advertisements.
    """
    job_ads = perform_post_request(
        url=f"{JOB_ADS_URL}/all",
        json=search_params.model_dump(mode="json"),
        params=filter_params.model_dump(),
    )
    logger.info(f"Retrieved {len(job_ads)} job ads")

    return [JobAdResponse(**job_ad) for job_ad in job_ads]


def get_by_id(job_ad_id: UUID) -> JobAdResponse:
    """
    Retrieve a job advertisement by its unique identifier.

    Args:
        job_ad_id (UUID): The unique identifier of the job advertisement.

    Returns:
        JobAdResponse: The job advertisement if found.
    """
    job_ad = perform_get_request(url=JOB_AD_BY_ID_URL.format(job_ad_id=job_ad_id))
    logger.info(f"Retrieved job ad with id {job_ad_id}")

    return JobAdResponse(**job_ad)


def create(
    company_id: UUID,
    job_ad_data: JobAdCreate,
) -> JobAdResponse:
    """
    Create a new job advertisement.

    Args:
        company_id (UUID): The unique identifier of the company creating the job advertisement.
        job_ad_data (JobAdCreate): The data required to create a new job advertisement.

    Returns:
        JobAdResponse: The created job advertisement.
    """
    job_ad_full_data = JobAdCreateFull(
        **job_ad_data.model_dump(), company_id=company_id
    )
    job_ad = perform_post_request(
        url=JOB_ADS_URL,
        json=job_ad_full_data.model_dump(mode="json"),
    )
    logger.info(f"Created job ad with id {job_ad['id']}")

    return JobAdResponse(**job_ad)


def update(
    job_ad_id: UUID,
    company_id: UUID,
    job_ad_data: JobAdUpdate,
) -> JobAdResponse:
    """
    Update a job advertisement with the given data.

    Args:
        job_ad_id (UUID): The unique identifier of the job advertisement to update.
        job_ad_data (JobAdUpdate): The data to update the job advertisement with.

    Returns:
        JobAdResponse: The updated job advertisement.
    """
    ensure_valid_job_ad_id(job_ad_id=job_ad_id, company_id=company_id)
    if job_ad_data.location is not None:
        ensure_valid_city(name=job_ad_data.location)

    job_ad = perform_put_request(
        url=JOB_AD_BY_ID_URL.format(job_ad_id=job_ad_id),
        json=job_ad_data.model_dump(mode="json"),
    )

    return JobAdResponse(**job_ad)


def add_skill_requirement(
    job_ad_id: UUID,
    skill_id: UUID,
) -> MessageResponse:
    """
    Add a skill requirement to a job advertisement.

    Args:
        job_ad_id (UUID): The unique identifier of the job advertisement.
        skill_id (UUID): The unique identifier of the skill to be added.

    Returns:
        MessageResponse: A response message indicating the result of the operation.
    """
    perform_post_request(
        url=JOB_AD_ADD_SKILL_URL.format(job_ad_id=job_ad_id, skill_id=skill_id),
    )
    logger.info(f"Added skill with id {skill_id} to job ad with id {job_ad_id}")

    return MessageResponse(message="Skill added to job ad")
