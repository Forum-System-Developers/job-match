import logging
from uuid import UUID

from fastapi import status
from sqlalchemy.orm import Session

from app.utils.database_utils import handle_database_operation
from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.skill import SkillBase
from app.sql_app.job_application_skill.job_application_skill import JobApplicationSkill
from app.sql_app.job_requirement.skill_level import SkillLevel
from app.sql_app.skill.skill import Skill

logger = logging.getLogger(__name__)


def create_skill(db: Session, skill_schema: SkillBase) -> SkillBase:
    """
    Creates a new Skill instance.

    Args:
        db (Session): Database dependency.
        skill_schema (SkillBase): Pydantic schema for collecting data.

    Returns:
        SkillBase: SkillBase Pydantic response model.
    """

    def _handle_create():
        skill_model: Skill = Skill(
            name=skill_schema.name,
            level=SkillLevel(skill_schema.level),
        )
        db.add(skill_model)
        db.commit()
        db.refresh(skill_model)
        logger.info(f"Skill {skill_model.name} created")

        return skill_schema

    return handle_database_operation(db_request=_handle_create, db=db)


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

    return handle_database_operation(db_request=_handle_create, db=db)


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
