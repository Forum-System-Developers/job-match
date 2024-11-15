import logging
from typing import Optional
from uuid import UUID

from fastapi import status
from sqlalchemy.orm import Session

from src.app.exceptions.custom_exceptions import ApplicationError
from src.app.schemas.job_ad import JobAdResponse
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
