import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.schemas.job_ad import JobAdCreate, JobAdResponse, JobAdUpdate
from app.services.utils.validators import (
    ensure_valid_company_id,
    ensure_valid_job_ad_id,
    ensure_valid_location,
)
from app.sql_app.job_ad.job_ad import JobAd
from app.sql_app.job_ad.job_ad_status import JobAdStatus

logger = logging.getLogger(__name__)


def get_all(db: Session, skip: int = 0, limit: int = 50) -> list[JobAdResponse]:
    """
    Retrieve all job advertisements.

    Args:
        db (Session): The database session used to query the job advertisements.
        skip (int): The number of job advertisements to skip.
        limit (int): The maximum number of job advertisements to retrieve.

    Returns:
        list[JobAdResponse]: The list of job advertisements.
    """
    job_ads = db.query(JobAd).offset(skip).limit(limit).all()
    logger.info(f"Retrieved {len(job_ads)} job ads")

    return [JobAdResponse.model_validate(job_ad) for job_ad in job_ads]


def get_by_id(id: UUID, db: Session) -> JobAdResponse:
    """
    Retrieve a job advertisement by its unique identifier.

    Args:
        id (UUID): The unique identifier of the job advertisement.
        db (Session): The database session used to query the job advertisement.

    Returns:
        Optional[JobAdResponse]: The job advertisement if found, otherwise None.
    """
    job_ad = ensure_valid_job_ad_id(id=id, db=db)
    logger.info(f"Retrieved job ad with id {id}")

    return JobAdResponse.model_validate(job_ad)


def create(job_ad_data: JobAdCreate, db: Session) -> JobAdResponse:
    """
    Create a new job advertisement.

    Args:
        job_ad_data (JobAdCreate): The data required to create a new job advertisement.
        db (Session): The database session used to create the job advertisement.

    Returns:
        JobAdResponse: The created job advertisement.

    Raises:
        ApplicationError: If the company or city is not found.
    """
    ensure_valid_company_id(id=job_ad_data.company_id, db=db)
    job_ad = JobAd(**job_ad_data.model_dump(), status=JobAdStatus.ACTIVE)

    db.add(job_ad)
    db.commit()
    db.refresh(job_ad)
    logger.info(f"Created job ad with id {job_ad.id}")

    return JobAdResponse.model_validate(job_ad)


def update(id: UUID, job_ad_data: JobAdUpdate, db: Session) -> JobAdResponse:
    """
    Update an existing job advertisement.

    Args:
        id (UUID): The unique identifier of the job advertisement to update.
        job_ad_data (JobAdUpdate): The data to update the job advertisement with.
        db (Session): The database session used to update the job advertisement.

    Returns:
        JobAdResponse: The updated job advertisement.

    Raises:
        ApplicationError: If the job advertisement, city, or company is not found.
    """
    job_ad = ensure_valid_job_ad_id(id=id, db=db)
    job_ad = _update_job_ad(job_ad_data=job_ad_data, job_ad=job_ad, db=db)

    if any(value is None for value in vars(job_ad_data).values()):
        job_ad.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(job_ad)
        logger.info(f"Job ad with id: {id} updated.")

    return JobAdResponse.model_validate(job_ad)


def _update_job_ad(job_ad_data: JobAdUpdate, job_ad: JobAd, db: Session) -> JobAd:
    """
    Updates the fields of a job advertisement based on the provided job_ad_data.

    Args:
        job_ad_data (JobAdUpdate): An object containing the updated data for the job advertisement.
        job_ad (JobAd): The job advertisement object to be updated.
        db (Session): The database session used for validating the location.

    Returns:
        JobAd: The updated job advertisement object.
    """
    if job_ad_data.location is not None:
        ensure_valid_location(location=job_ad_data.location, db=db)
        logger.info(f"Updated job ad (id: {id}) location to {job_ad_data.location}")

    if job_ad_data.title is not None:
        job_ad.title = job_ad_data.title
        logger.info(f"Updated job ad (id: {id}) title to {job_ad_data.title}")

    if job_ad_data.description is not None:
        job_ad.description = job_ad_data.description
        logger.info(
            f"Updated job ad (id: {id}) description to {job_ad_data.description}"
        )

    if job_ad_data.min_salary is not None:
        job_ad.min_salary = job_ad_data.min_salary
        logger.info(f"Updated job ad (id: {id}) min salary to {job_ad_data.min_salary}")

    if job_ad_data.max_salary is not None:
        job_ad.max_salary = job_ad_data.max_salary
        logger.info(f"Updated job ad (id: {id}) max salary to {job_ad_data.max_salary}")

    if job_ad_data.status is not None:
        job_ad.status = job_ad_data.status
        logger.info(f"Updated job ad (id: {id}) status to {job_ad_data.status}")

    return job_ad
