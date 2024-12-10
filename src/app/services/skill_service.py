import logging
from uuid import UUID

from app.schemas.skill import SkillCreate, SkillResponse
from app.services.external_db_service_urls import SKILLS_BY_CATEGORY_URL, SKILLS_URL
from app.utils.request_handlers import perform_get_request, perform_post_request

logger = logging.getLogger(__name__)


def create_skill(skill_data: SkillCreate) -> SkillResponse:
    """
    Creates a new skill by sending a POST request to the SKILLS_URL.

    Args:
        skill_data (SkillCreate): The data for the skill to be created.

    Returns:
        SkillResponse: The response containing the created skill's details.
    """
    skill = perform_post_request(
        url=SKILLS_URL,
        json=skill_data.model_dump(mode="json"),
    )
    logger.info(f"Skill {skill_data.name} created")

    return SkillResponse(**skill)


def get_for_category(category_id: UUID) -> list[SkillResponse]:
    """
    Retrieves all skills for a given category.

    Args:
        category_id (UUID): The unique identifier of the category.
    """
    skills = perform_get_request(
        url=SKILLS_BY_CATEGORY_URL.format(category_id=category_id)
    )

    return [SkillResponse(**skill) for skill in skills]
