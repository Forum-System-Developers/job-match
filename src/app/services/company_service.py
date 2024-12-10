import io
import logging
from uuid import UUID

from fastapi import UploadFile, status
from fastapi.responses import StreamingResponse

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.common import FilterParams, MessageResponse
from app.schemas.company import (
    CompanyCreate,
    CompanyCreateFinal,
    CompanyResponse,
    CompanyUpdate,
    CompanyUpdateFinal,
)
from app.schemas.user import User
from app.services.utils.common import get_company_by_phone_number
from app.services.utils.file_utils import validate_uploaded_file
from app.services.utils.validators import (
    ensure_valid_city,
    ensure_valid_company_id,
    is_unique_email,
    is_unique_username,
)
from app.utils.password_utils import hash_password
from app.utils.request_handlers import (
    perform_delete_request,
    perform_get_request,
    perform_post_request,
    perform_put_request,
)
from tests.services.urls import (
    COMPANIES_URL,
    COMPANY_BY_ID_URL,
    COMPANY_BY_USERNAME_URL,
    COMPANY_LOGO_URL,
    COMPANY_UPDATE_URL,
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
    Retrieve a User object based on the provided username.

    Args:
        username (str): The username of the company to retrieve.

    Returns:
        User: A User object containing the company's id, username, and password.
    """
    user = perform_get_request(url=COMPANY_BY_USERNAME_URL.format(username=username))
    logger.info(f"Retrieved company with username {username}")

    return User(**user)


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

    data = CompanyCreateFinal(
        **company_data.model_dump(exclude={"password", "city"}),
        password_hash=password_hash,
        city_id=city.id,
    )

    company = perform_post_request(url=COMPANIES_URL, json=data.model_dump(mode="json"))
    logger.info(f"Created company with id {company['id']}")

    return CompanyResponse(**company)


def update(
    company_id: UUID,
    company_data: CompanyUpdate,
) -> CompanyResponse:
    """
    Update the details of an existing company.

    Args:
        company_id (UUID): The unique identifier of the company to be updated.
        company_data (CompanyUpdate): The new data for the company.

    Returns:
        CompanyResponse: The response containing the updated company details.
    """
    company_update = _ensure_valid_company_update_data(
        company_id=company_id, company_data=company_data
    )

    company = perform_put_request(
        url=COMPANY_UPDATE_URL.format(company_id=company_id),
        json=company_update.model_dump(mode="json"),
    )
    logger.info(f"Updated company with id {company['id']}")

    return CompanyResponse(**company)


def upload_logo(company_id: UUID, logo: UploadFile) -> MessageResponse:
    """
    Uploads a logo for a specified company.

    Args:
        company_id (UUID): The unique identifier of the company.
        logo (UploadFile): The logo file to be uploaded.

    Returns:
        MessageResponse: A response message indicating the result of the upload operation.
    """
    validate_uploaded_file(logo)
    perform_post_request(
        url=COMPANY_LOGO_URL.format(company_id=company_id),
        files={"logo": (logo.filename, logo.file, logo.content_type)},
    )
    logger.info(f"Uploaded logo for company with id {company_id}")

    return MessageResponse(message="Logo uploaded successfully")


def download_logo(company_id: UUID) -> StreamingResponse:
    """
    Downloads the logo of a company.

    Args:
        company_id (UUID): The unique identifier of the company.

    Returns:
        StreamingResponse: A streaming response containing the company's logo.
    """
    ensure_valid_company_id(company_id=company_id)
    response = perform_get_request(url=COMPANY_LOGO_URL.format(company_id=company_id))

    logger.info(f"Downloaded logo of company with id {company_id}")

    return StreamingResponse(io.BytesIO(response.content), media_type="image/png")


def delete_logo(company_id: UUID) -> MessageResponse:
    """
    Deletes the logo of a company.

    Args:
        company_id (UUID): The unique identifier of the company.

    Returns:
        MessageResponse: A response message indicating the result of the delete operation.
    """
    ensure_valid_company_id(company_id=company_id)
    perform_delete_request(url=COMPANY_LOGO_URL.format(company_id=company_id))
    logger.info(f"Deleted logo of company with id {company_id}")

    return MessageResponse(message="Logo deleted successfully")


def _ensure_unique_email(email: str) -> None:
    """
    Ensure that the email is unique in the database.

    Args:
        email (str): The email to check.

    Raises:
        ApplicationError: If the email is not unique.
    """
    is_unique = is_unique_email(email=email)
    if not is_unique:
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
    Ensures that the provided company creation data is valid.

    Args:
        company_data (CompanyCreate): The data required to create a new company.
    """
    is_unique_username(username=company_data.username)
    is_unique_email(email=company_data.email)
    _ensure_unique_phone_number(phone_number=company_data.phone_number)


def _ensure_valid_company_update_data(
    company_id: UUID, company_data: CompanyUpdate
) -> CompanyUpdateFinal:
    """
    Ensures that the provided company id and update data are valid.

    Args:
        company_id (UUID): The unique identifier of the company.
        company_data (CompanyUpdate): The data to update the company with.

    Returns:
        CompanyUpdateFinal: The company update data.
    """
    company = ensure_valid_company_id(company_id=company_id)

    if company_data.city is not None:
        city = ensure_valid_city(name=company_data.city)

    if company_data.email is not None and company_data.email != company.email:
        _ensure_unique_email(email=company_data.email)

    if (
        company_data.phone_number is not None
        and company_data.phone_number != company.phone_number
    ):
        _ensure_unique_phone_number(phone_number=company_data.phone_number)

    return CompanyUpdateFinal(
        **company_data.model_dump(exclude={"city", "youtube_video_url"}, mode="json"),
        city_id=city.id if city else None,
    )
