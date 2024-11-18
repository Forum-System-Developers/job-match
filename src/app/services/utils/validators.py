import logging
from uuid import UUID

from fastapi import status
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.exceptions.custom_exceptions import ApplicationError
from app.sql_app.city.city import City
from app.sql_app.company.company import Company
from app.sql_app.job_ad.job_ad import JobAd
from app.sql_app.job_application.job_application import JobApplication
from app.sql_app.match.match import Match
from app.sql_app.match.match_status import MatchStatus

logger = logging.getLogger(__name__)


def ensure_valid_location(location: str, db: Session) -> City:
    """
    Ensures that the provided location exists in the database.

    Args:
        location (str): The name of the city to validate.
        db (Session): The database session to use for querying.

    Returns:
        City: The City object if the location is found in the database.

    Raises:
        ApplicationError: If the city with the given name is not found in the database.
    """
    city = db.query(City).filter(City.name == location).first()
    if city is None:
        logger.error(f"City with name {location} not found")
        raise ApplicationError(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"City with name {location} not found",
        )
    return city


def ensure_valid_job_ad_id(id: UUID, db: Session) -> JobAd:
    """
    Ensures that a JobAd with the given ID exists in the database.

    Args:
        id (UUID): The unique identifier of the JobAd.
        db (Session): The database session used to query the JobAd.

    Returns:
        JobAd: The JobAd object if found.

    Raises:
        ApplicationError: If no JobAd with the given ID is found, raises an error with a 404 status code.
    """
    job_ad = db.query(JobAd).filter(JobAd.id == id).first()
    if job_ad is None:
        logger.error(f"Job Ad with id {id} not found")
        raise ApplicationError(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job Ad with id {id} not found",
        )
    return job_ad


def ensure_valid_job_application_id(id: UUID, db: Session) -> JobApplication:
    job_application = db.query(JobApplication).filter(JobApplication.id == id).first()
    if job_application is None:
        logger.error(f"Job Application with id {id} not found")
        raise ApplicationError(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job Application with id {id} not found",
        )
    return job_application


def ensure_valid_company_id(id: UUID, db: Session) -> Company:
    """
    Ensures that a company with the given ID exists in the database.

    Args:
        id (UUID): The unique identifier of the company.
        db (Session): The database session to use for querying.

    Returns:
        Company: The company object if found.

    Raises:
        ApplicationError: If no company with the given ID is found, raises an error with a 404 status code.
    """
    company = db.query(Company).filter(Company.id == id).first()
    if company is None:
        logger.error(f"Company with id {id} not found")
        raise ApplicationError(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with id {id} not found",
        )
    return company
