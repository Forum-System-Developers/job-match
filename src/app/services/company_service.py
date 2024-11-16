import logging
from uuid import UUID

from fastapi import status
from sqlalchemy.orm import Session

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.company import CompanyCreate, CompanyResponse
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
