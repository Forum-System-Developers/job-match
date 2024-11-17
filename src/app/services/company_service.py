import logging
from uuid import UUID

from fastapi import status
from sqlalchemy.orm import Session

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.company import CompanyCreate, CompanyResponse, CompanyUpdate
from app.sql_app.company.company import Company

logger = logging.getLogger(__name__)


def get_all(db: Session, skip: int = 0, limit: int = 50) -> list[CompanyResponse]:
    """
    Retrieve a list of companies from the database with optional pagination.

    Args:
        db (Session): The database session to use for the query.
        skip (int, optional): The number of records to skip. Defaults to 0.
        limit (int, optional): The maximum number of records to return. Defaults to 50.

    Returns:
        List[CompanyResponse]: A list of company response models.
    """
    companies = db.query(Company).offset(skip).limit(limit).all()
    logger.info(f"Retrieved {len(companies)} companies")

    return [CompanyResponse.model_validate(company) for company in companies]


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

    return CompanyResponse.model_validate(company)


def create(company_data: CompanyCreate, db: Session) -> CompanyResponse:
    """
    Create a new company in the database.

    Args:
        company_data (CompanyCreate): The data required to create a new company.
        db (Session): The database session to use for the operation.

    Returns:
        CompanyResponse: The response object containing the created company's details.
    """
    _ensure_valid_company_creation_data(company_data=company_data, db=db)

    company = Company(**company_data.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    logger.info(f"Created company with id {company.id}")

    return CompanyResponse.model_validate(company)


def update(id: UUID, company_data: CompanyUpdate, db: Session) -> CompanyResponse:
    """
    Update an existing company in the database.

    Args:
        id (UUID): The unique identifier of the company to update.
        company_data (CompanyCreate): The data to update the company with.
        db (Session): The database session to use for the operation.

    Returns:
        CompanyResponse: The response object containing the updated company's details.
    """
    company = _ensure_company_exists(id=id, db=db)
    company = _update_company(company=company, company_data=company_data, db=db)

    db.commit()
    db.refresh(company)
    logger.info(f"Updated company with id {company.id}")

    return CompanyResponse.model_validate(company)


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
    company: Company, company_data: CompanyUpdate, db: Session
) -> Company:
    """
    Updates the company object with the provided company data.

    Args:
        company (Company): The company object to be updated.
        company_data (CompanyUpdate): The data to update the company with.
        db (Session): The database session to use for ensuring unique constraints.

    Returns:
        Company: The updated company object.
    """
    if company_data.name is not None:
        company.name = company_data.name
        logger.info(f"Updated company (id: {company.id}) name to {company_data.name}")

    if company_data.description is not None:
        company.description = company_data.description
        logger.info(
            f"Updated company (id: {company.id}) description to {company_data.description}"
        )

    # TODO: Update company address

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

    if company_data.logo is not None:
        company.logo = company_data.logo
        logger.info(f"Updated company (id: {company.id}) logo")

    return company


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
