import logging
from typing import Optional
from uuid import UUID

from fastapi import status
from sqlalchemy.orm import Session

from src.app.exceptions.custom_exceptions import ApplicationError
from src.app.schemas.job_ad import JobAdCreate, JobAdResponse
from src.app.sql_app.job_ad.job_ad import JobAd

logger = logging.getLogger(__name__)


def get_by_id(id: UUID, db: Session) -> JobAdResponse:
    """
    Retrieve a job advertisement by its unique identifier.

    Args:
        id (UUID): The unique identifier of the job advertisement.
        db (Session): The database session used to query the job advertisement.

    Returns:
        Optional[JobAdResponse]: The job advertisement if found, otherwise None.
    """
    job_ad = db.query(JobAd).filter(JobAd.id == id).first()
    if job_ad is None:
        logger.error(f"Job Ad with id {id} not found")
        raise ApplicationError(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job Ad with id {id} not found",
        )
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
        ApplicationError: If the company with the given ID is not found.
    """
    company = db.query(JobAd).filter(JobAd.company_id == job_ad_data.company_id).first()
    if company is None:
        logger.error(f"Company with id {job_ad_data.company_id} not found")
        raise ApplicationError(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with id {job_ad_data.company_id} not found",
        )

    job_ad = JobAd(**job_ad_data.model_dump())

    db.add(job_ad)
    db.commit()
    db.refresh(job_ad)
    logger.info(f"Created job ad with id {job_ad.id}")

    return JobAdResponse.model_validate(job_ad)
