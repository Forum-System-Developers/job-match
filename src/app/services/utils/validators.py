import logging
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.city import CityResponse
from app.schemas.company import CompanyResponse
from app.schemas.job_application import JobApplicationResponse
from app.services.enums.match_status import MatchStatus
from app.services.utils.common import (
    get_company_by_email,
    get_company_by_username,
    get_job_application_by_id,
    get_professional_by_email,
    get_professional_by_username,
)
from app.sql_app.city.city import City
from app.sql_app.company.company import Company
from app.sql_app.job_ad.job_ad import JobAd
from app.sql_app.job_application.job_application import JobApplication
from app.sql_app.match.match import Match
from app.sql_app.professional.professional import Professional
from app.sql_app.skill.skill import Skill
from app.utils.request_handlers import perform_get_request
from tests.services.urls import CITIES_URL, COMPANY_BY_ID_URL

logger = logging.getLogger(__name__)


def ensure_valid_city(name: str) -> CityResponse:
    """
    Ensure that a city with the given name exists.

    Args:
        name (str): The name of the city to validate.

    Returns:
        City: The City object if found.

    Raises:
        ApplicationError: If no city with the given name is found, raises an error with status code 404.
    """
    city = perform_get_request(f"{CITIES_URL}/by-name/{name}")
    return CityResponse(**city)


def ensure_valid_job_ad_id(
    job_ad_id: UUID, db: Session, company_id: UUID | None = None
) -> JobAd:
    """
    Ensures that the provided job advertisement ID is valid and optionally belongs to the specified company.
    Args:
        job_ad_id (UUID): The unique identifier of the job advertisement.
        db (Session): The database session to use for querying.
        company_id (UUID | None, optional): The unique identifier of the company to which the job advertisement should belong. Defaults to None.
    Returns:
        JobAd: The job advertisement object if it is found and valid.
    Raises:
        ApplicationError: If the job advertisement is not found or does not belong to the specified company.
    """
    job_ad = db.query(JobAd).filter(JobAd.id == job_ad_id).first()
    if job_ad is None:
        logger.error(f"Job Ad with id {job_ad_id} not found")
        raise ApplicationError(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job Ad with id {job_ad_id} not found",
        )
    if company_id is not None and job_ad.company_id != company_id:
        logger.error(
            f"Job Ad with id {job_ad_id} does not belong to company with id {company_id}"
        )
        raise ApplicationError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job Ad with id {job_ad_id} does not belong to company with id {company_id}",
        )

    return job_ad


def ensure_valid_job_application_id(
    job_application_id: UUID, professional_id: UUID | None = None
) -> JobApplicationResponse:
    """
    Ensures that a job application with the given ID exists and optionally
    belongs to the specified professional.

    Args:
        job_application_id (UUID): The ID of the job application to validate.
        professional_id (UUID | None, optional): The ID of the professional
            to validate ownership. Defaults to None.

    Returns:
        JobApplication: The validated job application object.

    Raises:
        ApplicationError: If the job application does not exist or does not
            belong to the specified professional.
    """
    job_application = get_job_application_by_id(job_application_id=job_application_id)
    if job_application is None:
        logger.error(f"Job Application with id {job_application_id} not found")
        raise ApplicationError(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job Application with id {job_application_id} not found",
        )
    if (
        professional_id is not None
        and job_application.professional_id != professional_id
    ):
        logger.error(
            f"Job Application with id {job_application_id} does not belong to professional with id {professional_id}"
        )
        raise ApplicationError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job Application with id {job_application_id} does not belong to professional with id {professional_id}",
        )
    return job_application


def ensure_valid_company_id(company_id: UUID) -> CompanyResponse:
    """
    Ensures that the given company ID is valid by performing a GET request to retrieve the company details.

    Args:
        company_id (UUID): The unique identifier of the company.

    Returns:
        CompanyResponse: The response object containing the company details.

    Raises:
        HTTPError: If the GET request fails or the company is not found.
    """
    company = perform_get_request(url=COMPANY_BY_ID_URL.format(company_id=company_id))
    logger.info(f"Company with id {company_id} found")

    return CompanyResponse(**company)


def ensure_no_match_request(
    job_ad_id: UUID, job_application_id: UUID, db: Session
) -> None:
    """
    Ensures that there is no existing match request between the given job advertisement
    and job application in the database.

    Args:
        job_ad_id (UUID): The unique identifier of the job advertisement.
        job_application_id (UUID): The unique identifier of the job application.
        db (Session): The database session used to query the Match table.

    Raises:
        ApplicationError: If a match request already exists between the given job advertisement
                          and job application, an ApplicationError is raised with a 400 status code.
    """
    match = (
        db.query(Match)
        .filter(
            and_(
                Match.job_ad_id == job_ad_id,
                Match.job_application_id == job_application_id,
            )
        )
        .first()
    )
    if match is not None:
        logger.error(
            f"Match request already exists between job ad {job_ad_id} and job application {job_application_id}"
        )
        raise ApplicationError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Match request between job ad with id {job_ad_id} and job application with id {job_application_id} already exists",
        )


def ensure_valid_match_request(
    job_ad_id: UUID,
    job_application_id: UUID,
    match_status: MatchStatus,
    db: Session,
) -> Match:
    """
    Ensures that a match request exists and is in the REQUESTED status.

    Args:
        job_ad_id (UUID): The ID of the job advertisement.
        job_application_id (UUID): The ID of the job application.
        match_status (MatchStatus): The status of the match request.
        db (Session): The database session.

    Returns:
        Match: The match object if it exists and is in the REQUESTED status.

    Raises:
        ApplicationError: If the match request is not found or is not in the REQUESTED status.
    """
    match = (
        db.query(Match)
        .filter(
            and_(
                Match.job_ad_id == job_ad_id,
                Match.job_application_id == job_application_id,
            )
        )
        .first()
    )
    if match is None:
        logger.error(
            f"Match request with job ad id {job_ad_id} and job application id {job_application_id} not found"
        )
        raise ApplicationError(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match request with job ad id {job_ad_id} and job application id {job_application_id} not found",
        )
    if match.status != match_status:
        logger.error(
            f"Match request with job ad id {job_ad_id} and job application id {job_application_id} is in {match.status} status - requires {match_status.name} status"
        )
        raise ApplicationError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Match request with job ad id {job_ad_id} and job application id {job_application_id} is not in {match_status.name} status",
        )

    return match


def ensure_valid_skill_id(
    skill_id: UUID,
    category_id: UUID,
    db: Session,
) -> Skill:
    """
    Ensure that a skill with the given skill_id and category_id exists in the database.

    Args:
        skill_id (UUID): The unique identifier of the skill.
        category_id (UUID): The unique identifier of the category to which the skill belongs.
        db (Session): The database session used to query the skill.

    Returns:
        Skill: The skill object if found.

    Raises:
        ApplicationError: If the skill with the given skill_id and category_id is not found.
    """
    skill = (
        db.query(Skill)
        .filter(
            and_(
                Skill.id == skill_id,
                Skill.category_id == category_id,
            )
        )
        .first()
    )
    if skill is None:
        logger.error(f"Skill with id {skill_id} not found")
        raise ApplicationError(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill with id {skill_id} not found",
        )

    return skill


def is_unique_username(username: str) -> bool:
    professional = get_professional_by_username(username)
    if professional is not None:
        return False

    company = get_company_by_username(username)
    if company is not None:
        return False

    return True


def is_unique_email(email: str) -> bool:
    professional = get_professional_by_email(email)
    if professional is not None:
        return False

    company = get_company_by_email(email)
    if company is not None:
        return False

    return True


def ensure_valid_professional_id(professional_id: UUID, db: Session) -> Professional:
    professional = (
        db.query(Professional).filter(Professional.id == professional_id).first()
    )
    if professional is None:
        raise ApplicationError(
            detail=f"Professional with id {professional_id} not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return professional
