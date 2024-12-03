import logging
from uuid import UUID

from fastapi import status
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.skill import Skill, SkillCreate, SkillResponse
from app.sql_app.job_ad_skill.job_ad_skill import JobAdSkill
from app.sql_app.job_application_skill.job_application_skill import JobApplicationSkill
from app.sql_app.job_requirement.skill_level import SkillLevel
from app.sql_app.pending_skill.pending_skill import PendingSkill
from app.sql_app.skill.skill import Skill
from app.utils.processors import process_db_transaction

logger = logging.getLogger(__name__)


def create_skill(db: Session, skill_data: SkillCreate) -> UUID:
    """
    Creates a new Skill instance.

    Args:
        db (Session): Database dependency.
        skill_schema (SkillBase): Pydantic schema for collecting data.

    Returns:
        UUID: The ID of the newly created Skill.
    """

    def _handle_create() -> UUID:
        skill_model: Skill = Skill(
            name=skill_data.name,
            category_id=skill_data.category_id,
        )
        db.add(skill_model)
        db.commit()
        db.refresh(skill_model)
        logger.info(f"Skill {skill_model.name} created")

        return skill_model.id

    return process_db_transaction(transaction_func=_handle_create, db=db)


def create_job_application_skill(
    db: Session, skill_id: UUID, job_application_id: UUID
) -> UUID:
    """
    Creates a new Job Application Skill instance.

    Args:
        db (Session): Database dependency.
        skill_id (UUID): Identifier for the skill.
        application_id (UUID): Identifier for the application.

    Returns:
        UUID: Identifier for the skill.
    """

    def _handle_create():
        job_application_skill = JobApplicationSkill(
            job_application_id=job_application_id,
            skill_id=skill_id,
        )

        db.add(job_application_skill)
        db.commit()
        db.refresh(job_application_skill)

        logger.info(f"Job Application skill id {skill_id} created")
        return skill_id

    return process_db_transaction(transaction_func=_handle_create, db=db)


def create_pending_skill(
    company_id: UUID,
    skill_data: SkillCreate,
    db: Session,
) -> SkillResponse:
    """
    Creates a pending skill entry in the database.

    Args:
        company_id (UUID): The ID of the company submitting the skill.
        skill_data (SkillCreate): The data of the skill to be created.
        db (Session): The database session.

    Returns:
        SkillResponse: The response containing the details of the created pending skill.

    Raises:
        ApplicationError: If the skill already exists in the database.
    """
    if exists(
        skill_name=skill_data.name,
        db=db,
    ):
        logger.error(f"Skill {skill_data.name} already exists")
        raise ApplicationError(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Skill {skill_data.name} already exists",
        )

    pending_skill = PendingSkill(
        name=skill_data.name,
        category_id=skill_data.category_id,
        submitted_by=company_id,
    )

    db.add(pending_skill)
    db.commit()
    db.refresh(pending_skill)

    logger.info(f"Pending skill {pending_skill.name} created")

    return SkillResponse(
        id=pending_skill.id,
        name=pending_skill.name,
        category_id=pending_skill.category_id,
    )


def exists(db: Session, skill_name: str) -> bool:
    """
    Verifies if a Skill already exists in the database.

    Args:
        db (Session): Database dependency.
        skill_name (str): The name of the skill.

    Returns:
        bool
    """
    query = db.query(Skill).filter(Skill.name == skill_name).first()
    return query is not None


def get_id(db: Session, skill_name: str) -> UUID:
    """
    Fetches the identifier of a Skill by its name.

    Args:
        db (Session): Database dependency.
        skill_name (str): The name of the skill.

    Returns:
        UUID
    """
    skill = db.query(Skill).filter(Skill.name == skill_name).first()
    if skill is None:
        raise ApplicationError(
            detail=f"Skill with name {skill_name} not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return skill.id


def get_by_id(skill_id: UUID, db: Session) -> SkillResponse:
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if skill is None:
        raise ApplicationError(
            detail=f"Skill with id {skill_id} not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return SkillResponse.create(skill)
