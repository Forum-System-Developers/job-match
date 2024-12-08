import io
import logging
from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.common import FilterParams, MessageResponse
from app.schemas.company import (
    CompanyCreate,
    CompanyCreateComplete,
    CompanyResponse,
    CompanyUpdate,
)
from app.schemas.user import User
from app.services.utils.common import get_company_by_phone_number
from app.services.utils.file_utils import handle_file_upload
from app.services.utils.validators import (
    ensure_valid_city,
    ensure_valid_company_id,
    is_unique_email,
    is_unique_username,
)
from app.sql_app.company.company import Company
from app.utils.password_utils import hash_password
from app.utils.request_handlers import perform_get_request, perform_post_request
from tests.services.urls import (
    COMPANIES_URL,
    COMPANY_BY_EMAIL_URL,
    COMPANY_BY_ID_URL,
    COMPANY_BY_PHONE_NUMBER_URL,
    COMPANY_BY_USERNAME_URL,
)

logger = logging.getLogger(__name__)


def get_all(filter_params: FilterParams) -> list[CompanyResponse]:
    """
    Retrieve a list of companies from the database based on the provided filter parameters.

    Args:
        filter_params (FilterParams): The parameters to filter the companies, including offset and limit.

    Returns:
        list[CompanyResponse]: A list of CompanyResponse objects representing the retrieved companies.
    """
    companies = perform_get_request(
        url=COMPANIES_URL, params=filter_params.model_dump()
    )
    logger.info(f"Retrieved {len(companies)} companies")

    return [CompanyResponse(**company) for company in companies]


def get_by_id(company_id: UUID) -> CompanyResponse:
    """
    Retrieve a company by its unique identifier.

    Args:
        company_id (UUID): The unique identifier of the company.

    Returns:
        CompanyResponse: The company response model.
    """
    company = perform_get_request(url=COMPANY_BY_ID_URL.format(company_id=company_id))
    logger.info(f"Retrieved company with id {company_id}")

    return CompanyResponse(**company)


def get_by_username(username: str) -> User:
    """
    Retrieve a company by its username.

    Args:
        username (str): The username of the company to retrieve.

    Returns:
        User: A User object representing the retrieved company.

    Raises:
        ApplicationError: If no company with the given username is found.
    """
    company = perform_get_request(url=COMPANY_BY_USERNAME_URL.format(username=username))
    logger.info(f"Retrieved company with username {username}")

    return User(id=company.id, username=company.username, password=company.password)


def create(company_data: CompanyCreate) -> CompanyResponse:
    """
    Create a new company record in the database.

    Args:
        company_data (CompanyCreate): The data required to create a new company.

    Returns:
        CompanyResponse: The response object containing the created company details.
    """
    _ensure_valid_company_creation_data(company_data=company_data)
    city = ensure_valid_city(name=company_data.city)

    password_hash = hash_password(company_data.password)

    data = CompanyCreateComplete(
        **company_data.model_dump(exclude={"password", "city"}),
        password_hash=password_hash,
        city_id=city.id,
    )

    company = perform_post_request(url=COMPANIES_URL, json=data.model_dump(mode="json"))
    logger.info(f"Created company with id {company['id']}")

    return CompanyResponse(**company)


def update(
    id: UUID,
    company_data: CompanyUpdate,
    db: Session,
) -> CompanyResponse:
    """
    Update an existing company in the database.

    Args:
        id (UUID): The unique identifier of the company to update.
        company_data (CompanyCreate): The data to update the company with.
        db (Session): The database session to use for the operation.

    Returns:
        CompanyResponse: The response object containing the updated company's details.
    """
    company = ensure_valid_company_id(id=id, db=db)
    company = _update_company(company=company, company_data=company_data, db=db)

    db.commit()
    db.refresh(company)
    logger.info(f"Updated company with id {company.id}")

    return CompanyResponse.create(company)


def upload_logo(company_id: UUID, logo: UploadFile, db: Session) -> MessageResponse:
    """
    Uploads a logo for a specified company.

    Args:
        company_id (UUID): The unique identifier of the company.
        logo (UploadFile): The logo file to be uploaded.
        db (Session): The database session.

    Returns:
        MessageResponse: A response message indicating the result of the upload operation.
    """
    company = ensure_valid_company_id(id=company_id, db=db)
    company.logo = handle_file_upload(logo)
    company.updated_at = datetime.now()
    db.commit()
    logger.info(f"Uploaded logo for company with id {company_id}")

    return MessageResponse(message="Logo uploaded successfully")


def download_logo(company_id: UUID, db: Session) -> StreamingResponse:
    """
    Downloads the logo of a company.
    Args:
        company_id (UUID): The unique identifier of the company.
        db (Session): The database session.
    Returns:
        StreamingResponse: A streaming response containing the company's logo.
    Raises:
        ApplicationError: If the company does not have a logo or does not exist.
    """
    company = ensure_valid_company_id(id=company_id, db=db)
    logo = company.logo
    if logo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with id {company_id} does not have a logo",
        )
    logger.info(f"Downloaded logo of company with id {company_id}")

    return StreamingResponse(io.BytesIO(logo), media_type="image/png")


def delete_logo(company_id: UUID, db: Session) -> MessageResponse:
    """
    Deletes the logo of a company.
    Args:
        company_id (UUID): The unique identifier of the company.
        db (Session): The database session.
    Returns:
        MessageResponse: A response message indicating the result of the delete operation.
    Raises:
        ApplicationError: If the company does not have a logo or does not exist.
    """
    company = ensure_valid_company_id(id=company_id, db=db)
    if company.logo is None:
        raise ApplicationError(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with id {company_id} does not have a logo",
        )
    company.logo = None
    company.updated_at = datetime.now()
    db.commit()
    logger.info(f"Deleted logo of company with id {company_id}")

    return MessageResponse(message="Logo deleted successfully")


def _update_company(
    company: Company,
    company_data: CompanyUpdate,
    db: Session,
) -> Company:
    """
    Updates the details of a company with the provided data.
    Args:
        company (Company): The company instance to be updated.
        company_data (CompanyUpdate): The data to update the company with.
        db (Session): The database session to use for any database operations.
    Returns:
        Company: The updated company instance.
    """
    if company_data.name is not None:
        company.name = company_data.name
        logger.info(f"Updated company (id: {company.id}) name to {company_data.name}")

    if company_data.description is not None:
        company.description = company_data.description
        logger.info(
            f"Updated company (id: {company.id}) description to {company_data.description}"
        )

    if company_data.address_line is not None:
        company.address_line = company_data.address_line
        logger.info(
            f"Updated company (id: {company.id}) address_line to {company_data.address_line}"
        )

    if company_data.city is not None:
        city = ensure_valid_city(name=company_data.city)
        company.city = city
        logger.info(f"Updated company (id: {company.id}) city to {city.name}")

    if company_data.email is not None:
        _ensure_unique_email(email=company_data.email)
        company.email = company_data.email
        logger.info(f"Updated company (id: {company.id}) email to {company_data.email}")

    if company_data.phone_number is not None:
        _ensure_unique_phone_number(phone_number=company_data.phone_number)
        company.phone_number = company_data.phone_number
        logger.info(
            f"Updated company (id: {company.id}) phone number to {company_data.phone_number}"
        )

    if company_data.website_url is not None:
        company.website_url = str(company_data.website_url)
        logger.info(
            f"Updated company (id: {company.id}) website URL to {company_data.website_url}"
        )

    if company_data.youtube_video_id is not None:
        company.youtube_video_id = company_data.youtube_video_id
        logger.info(
            f"Updated company (id: {company.id}) YouTube video ID to {company_data.youtube_video_id}"
        )

    if any(value is not None for value in vars(company_data).values()):
        company.updated_at = datetime.now()

    return company


def _ensure_unique_email(email: str) -> None:
    """
    Ensure that the email is unique in the database.

    Args:
        email (str): The email to check.

    Raises:
        ApplicationError: If the email is not unique.
    """
    company = perform_get_request(url=COMPANY_BY_EMAIL_URL.format(email=email))
    if company is not None:
        logger.error(f"Company with email {email} already exists")
        raise ApplicationError(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Company with email {email} already exists",
        )


def _ensure_unique_phone_number(phone_number: str) -> None:
    """
    Ensure that the phone number is unique in the database.

    Args:
        phone_number (str): The phone number to check.

    Raises:
        ApplicationError: If the phone number is not unique.
    """
    company = get_company_by_phone_number(phone_number=phone_number)
    if company is not None:
        logger.error(f"Company with phone number {phone_number} already exists")
        raise ApplicationError(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Company with phone number {phone_number} already exists",
        )


def _ensure_valid_company_creation_data(company_data: CompanyCreate) -> None:
    """
    Ensure that the company data is valid for creation.

    Args:
        company_data (CompanyCreate): The company data to validate.

    Raises:
        ApplicationError: If the company data is invalid.
    """
    is_unique_username(username=company_data.username)
    is_unique_email(email=company_data.email)
    _ensure_unique_phone_number(phone_number=company_data.phone_number)
