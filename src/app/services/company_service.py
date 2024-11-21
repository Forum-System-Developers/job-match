import io
import logging
from datetime import datetime
from uuid import UUID

from fastapi import UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.common import FilterParams, MessageResponse
from app.schemas.company import CompanyCreate, CompanyResponse, CompanyUpdate
from app.schemas.user import User
from app.services import city_service
from app.services.utils.validators import ensure_valid_company_id
from app.sql_app.city.city import City
from app.sql_app.company.company import Company
from app.utils.password_utils import hash_password

logger = logging.getLogger(__name__)


def get_all(filter_params: FilterParams, db: Session) -> list[CompanyResponse]:
    """
    Retrieve a list of companies from the database based on the provided filter parameters.

    Args:
        filter_params (FilterParams): The parameters to filter the companies, including offset and limit.
        db (Session): The database session used to query the companies.

    Returns:
        list[CompanyResponse]: A list of CompanyResponse objects representing the retrieved companies.
    """
    companies = (
        db.query(Company).offset(filter_params.offset).limit(filter_params.limit).all()
    )
    logger.info(f"Retrieved {len(companies)} companies")

    return [CompanyResponse.create(company) for company in companies]


def get_by_id(id: UUID, db: Session) -> CompanyResponse:
    """
    Retrieve a company by its unique identifier.

    Args:
        id (UUID): The unique identifier of the company.
        db (Session): The database session to use for the query.

    Returns:
        CompanyResponse: The company response model.
    """
    company = _ensure_company_exists(id=id, db=db)
    logger.info(f"Retrieved company with id {id}")

    return CompanyResponse.create(company)


def get_by_username(username: str, db: Session) -> User:
    """
    Retrieve a company by its username.

    Args:
        username (str): The username of the company to retrieve.
        db (Session): The database session to use for the query.

    Returns:
        User: A User object representing the retrieved company.

    Raises:
        ApplicationError: If no company with the given username is found.
    """
    company = _get_by_username(username=username, db=db)
    if company is None:
        logger.error(f"Company with username {username} not found")
        raise ApplicationError(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with username {username} not found",
        )
    logger.info(f"Retrieved company with username {username}")

    return User(id=company.id, username=company.username, password=company.password)


def create(
    company_data: CompanyCreate, db: Session, logo: UploadFile | None = None
) -> CompanyResponse:
    """
    Create a new company record in the database.

    Args:
        company_data (CompanyCreate): The data required to create a new company.
        db (Session): The database session to use for the operation.
        logo (UploadFile | None, optional): An optional logo file for the company. Defaults to None.

    Returns:
        CompanyResponse: The response object containing the created company details.
    """
    _ensure_valid_company_creation_data(company_data=company_data, db=db)
    city = _ensure_valid_city(city_name=company_data.city, db=db)

    upload_logo = None
    if logo is not None:
        upload_logo = logo.file.read()

    password_hash = hash_password(company_data.password)

    company = Company(
        **company_data.model_dump(exclude={"password", "city"}),
        password=password_hash,
        city_id=city.id,
        logo=upload_logo,
    )

    db.add(company)
    db.commit()
    db.refresh(company)
    logger.info(f"Created company with id {company.id}")

    return CompanyResponse.create(company)


def update(
    id: UUID, company_data: CompanyUpdate, db: Session, logo: UploadFile | None = None
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
    company = _update_company(
        company=company, company_data=company_data, logo=logo, db=db
    )

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
    upload_logo = logo.file.read()
    company.logo = upload_logo
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
    company = _ensure_company_exists(id=company_id, db=db)
    logo = company.logo
    if logo is None:
        raise ApplicationError(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with id {company_id} does not have a logo",
        )
    logger.info(f"Downloaded logo of company with id {company_id}")

    return StreamingResponse(io.BytesIO(logo), media_type="image/png")


def _get_by_id(id: UUID, db: Session) -> Company | None:
    """
    Retrieve a company by its ID from the database.

    Args:
        id (UUID): The unique identifier of the company.
        db (Session): The database session used to query the company.

    Returns:
        Company: The company object if found, otherwise None.
    """
    return db.query(Company).filter(Company.id == id).first()


def _get_by_username(username: str, db: Session) -> Company | None:
    """
    Retrieve a company by its username from the database.

    Args:
        username (str): The username of the company.
        db (Session): The database session used to query the company.

    Returns:
        Company: The company object if found, otherwise None.
    """
    return db.query(Company).filter(Company.username == username).first()


def _get_by_email(email: str, db: Session) -> Company | None:
    """
    Retrieve a company by its email from the database.

    Args:
        email (str): The email of the company.
        db (Session): The database session used to query the company.

    Returns:
        Company: The company object if found, otherwise None.
    """
    return db.query(Company).filter(Company.email == email).first()


def _get_by_phone_number(phone_number: str, db: Session) -> Company | None:
    """
    Retrieve a company by its phone number from the database.

    Args:
        phone_number (str): The phone number of the company.
        db (Session): The database session used to query the company.

    Returns:
        Company: The company object if found, otherwise None.
    """
    return db.query(Company).filter(Company.phone_number == phone_number).first()


def _update_company(
    company: Company,
    company_data: CompanyUpdate,
    db: Session,
    logo: UploadFile | None = None,
) -> Company:
    """
    Updates the details of a company with the provided data.
    Args:
        company (Company): The company instance to be updated.
        company_data (CompanyUpdate): The data to update the company with.
        db (Session): The database session to use for any database operations.
        logo (UploadFile | None, optional): The new logo file to update, if any. Defaults to None.
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
        city = _ensure_valid_city(city_name=company_data.city, db=db)
        company.city = city
        logger.info(f"Updated company (id: {company.id}) city to {city.name}")

    if company_data.email is not None:
        _ensure_unique_email(email=company_data.email, db=db)
        company.email = company_data.email
        logger.info(f"Updated company (id: {company.id}) email to {company_data.email}")

    if company_data.phone_number is not None:
        _ensure_unique_phone_number(phone_number=company_data.phone_number, db=db)
        company.phone_number = company_data.phone_number
        logger.info(
            f"Updated company (id: {company.id}) phone number to {company_data.phone_number}"
        )

    if logo is not None:
        upload_logo = logo.file.read()
        company.logo = upload_logo
        logger.info(f"Updated company (id: {company.id}) logo")

    if any(value is None for value in vars(company_data).values()) or logo is not None:
        company.updated_at = datetime.now()
        logger.info(f"Updated job ad (id: {id}) updated_at to job_ad.updated_at")

    return company


def _ensure_valid_city(city_name: str, db: Session) -> City:
    """
    Ensures that the given city name is valid by retrieving it from the database.

    Args:
        city_name (str): The name of the city to validate.
        db (Session): The database session to use for the query.

    Returns:
        City: A City object containing the ID and name of the validated city.

    """
    city = city_service.get_by_name(city_name=city_name, db=db)
    return City(**city.model_dump())


def _ensure_unique_email(email: str, db: Session) -> None:
    """
    Ensure that the email is unique in the database.

    Args:
        email (str): The email to check.
        db (Session): The database session used to query the company.

    Raises:
        ApplicationError: If the email is not unique.
    """
    company = _get_by_email(email=email, db=db)
    if company is not None:
        logger.error(f"Company with email {email} already exists")
        raise ApplicationError(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Company with email {email} already exists",
        )


def _ensure_unique_username(username: str, db: Session) -> None:
    """
    Ensure that the username is unique in the database.

    Args:
        username (str): The username to check.
        db (Session): The database session used to query the company.

    Raises:
        ApplicationError: If the username is not unique.
    """
    company = _get_by_username(username=username, db=db)
    if company is not None:
        logger.error(f"Company with username {username} already exists")
        raise ApplicationError(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Company with username {username} already exists",
        )


def _ensure_unique_phone_number(phone_number: str, db: Session) -> None:
    """
    Ensure that the phone number is unique in the database.

    Args:
        phone_number (str): The phone number to check.
        db (Session): The database session used to query the company.

    Raises:
        ApplicationError: If the phone number is not unique.
    """
    company = _get_by_phone_number(phone_number=phone_number, db=db)
    if company is not None:
        logger.error(f"Company with phone number {phone_number} already exists")
        raise ApplicationError(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Company with phone number {phone_number} already exists",
        )


def _ensure_company_exists(id: UUID, db: Session) -> Company:
    """
    Ensure that a company exists in the database.

    Args:
        id (UUID): The unique identifier of the company.
        db (Session): The database session used to query the company.

    Raises:
        ApplicationError: If the company does not exist.
    """
    company = _get_by_id(id=id, db=db)
    if company is None:
        logger.error(f"Company with id {id} not found")
        raise ApplicationError(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with id {id} not found",
        )

    return company


def _ensure_valid_company_creation_data(
    company_data: CompanyCreate, db: Session
) -> None:
    """
    Ensure that the company data is valid for creation.

    Args:
        company_data (CompanyCreate): The company data to validate.
        db (Session): The database session used to query the company.

    Raises:
        ApplicationError: If the company data is invalid.
    """
    _ensure_unique_username(username=company_data.username, db=db)
    _ensure_unique_email(email=company_data.email, db=db)
    _ensure_unique_phone_number(phone_number=company_data.phone_number, db=db)
