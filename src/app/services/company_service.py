import logging
from uuid import UUID

from fastapi import status
from sqlalchemy.orm import Session

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.company import CompanyResponse
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
    company = db.query(Company).filter(Company.id == id).first()
    if company is None:
        logger.error(f"Company with id {id} not found")
        raise ApplicationError(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with id {id} not found",
        )
    logger.info(f"Retrieved company with id {id}")

    return CompanyResponse.model_validate(company)
