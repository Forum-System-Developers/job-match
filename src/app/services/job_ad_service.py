from typing import Optional
from uuid import UUID

from fastapi import status
from sqlalchemy.orm import Session

from app.exceptions.custom_exceptions import ApplicationError
from app.sql_app.job_ad.job_ad import JobAd
from app.utils.logger import get_logger

logger = get_logger(__name__)


def get_by_id(id: UUID, db: Session) -> Optional[JobAd]:
    """
    Retrieve a job advertisement by its unique identifier.

    Args:
        id (UUID): The unique identifier of the job advertisement.
        db (Session): The database session used to query the job advertisement.

    Returns:
        Optional[JobAd]: The job advertisement if found, otherwise None.
    """
    job_ad = db.query(JobAd).filter(JobAd.id == id).first()
    if job_ad is None:
        logger.error(f"Job Ad with id {id} not found")
        raise ApplicationError(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job Ad with id {id} not found",
        )
    logger.info(f"Retrieved job ad with id {id}")

    return job_ad
