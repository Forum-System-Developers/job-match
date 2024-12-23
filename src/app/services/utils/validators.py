import logging
from uuid import UUID

from fastapi import status

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.city import CityResponse
from app.schemas.company import CompanyResponse
from app.schemas.job_ad import JobAdResponse
from app.schemas.job_application import JobApplicationResponse
from app.schemas.professional import ProfessionalResponse
from app.services.enums.match_status import MatchStatus
from app.services.external_db_service_urls import CITIES_URL, COMPANY_BY_ID_URL
from app.services.utils.common import (
    get_company_by_email,
    get_company_by_username,
    get_job_ad_by_id,
    get_job_application_by_id,
    get_match_request_by_id,
    get_professional_by_email,
    get_professional_by_id,
    get_professional_by_username,
)
from app.utils.request_handlers import perform_get_request

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
    job_ad_id: UUID,
    company_id: UUID | None = None,
) -> JobAdResponse:
    """
    Ensures that the provided job advertisement ID is valid and optionally
    belongs to the specified company.

    Args:
        job_ad_id (UUID): The unique identifier of the job advertisement.
        company_id (UUID | None, optional): The unique identifier of the company.
            Defaults to None.

    Returns:
        JobAdResponse: The job advertisement details if the ID is valid.

    Raises:
        ApplicationError: If the job advertisement is not found or does not
            belong to the specified company.
    """
    job_ad = get_job_ad_by_id(job_ad_id=job_ad_id)
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
    job_ad_id: UUID,
    job_application_id: UUID,
) -> None:
    """
    Ensures that there is no existing match request between the given job advertisement
    and job application in the database.

    Args:
        job_ad_id (UUID): The unique identifier of the job advertisement.
        job_application_id (UUID): The unique identifier of the job application.

    Raises:
        ApplicationError: If a match request already exists between the given job advertisement
                          and job application, an ApplicationError is raised with a 400 status code.
    """
    match = get_match_request_by_id(
        job_ad_id=job_ad_id, job_application_id=job_application_id
    )
    if match is not None:
        logger.error(
            f"Match request already exists between job ad {job_ad_id} and job application {job_application_id}"
        )
        raise ApplicationError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Match request between job ad with id {job_ad_id} and job application with id {job_application_id} already exists",
        )


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
