import logging
from uuid import UUID

from fastapi import status
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.requirement import RequirementCreate, RequirementResponse
from app.sql_app.job_requirement.job_requirement import JobRequirement

logger = logging.getLogger(__name__)


def create(
    company_id: UUID, requirement_data: RequirementCreate, db: Session
) -> RequirementResponse:
    """
    Create a new job requirement.

    Args:
        requirement (RequirementCreate): Pydantic schema for collecting data.
        db (Session): Database dependency.

    Returns:
        JobRequirement: JobRequirement SQLAlchemy model.
    """
    if _exists(
        company_id=company_id,
        requirement_description=requirement_data.description,
        db=db,
    ):
        logger.error(
            f"Requirement {requirement_data.description} for company id {company_id} already exists"
        )
        raise ApplicationError(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Requirement {requirement_data.description} already exists",
        )

    requirement_model = JobRequirement(
        description=requirement_data.description,
        skill_level=requirement_data.skill_level,
        company_id=company_id,
    )

    db.add(requirement_model)
    db.commit()
    db.refresh(requirement_model)

    logger.info(f"Requirement {requirement_model.description} created")

    return RequirementResponse.create(requirement_model)


def _exists(company_id: UUID, requirement_description: str, db: Session) -> bool:
    """
    Check if a job requirement exists by its name and company_id.

    Args
        company_id (UUID): The unique identifier of the company.
        requirement_name (str): The name of the requirement.
        db (Session): Database dependency.

    Returns:
        bool: True if the requirement exists, False otherwise.
    """
    return (
        db.query(JobRequirement)
        .filter(
            and_(
                JobRequirement.company_id == company_id,
                JobRequirement.description == requirement_description,
            )
        )
        .first()
        is not None
    )
