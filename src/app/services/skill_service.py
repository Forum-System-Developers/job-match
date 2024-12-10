import logging

from app.schemas.skill import SkillCreate, SkillResponse
from app.services.external_db_service_urls import SKILLS_URL
from app.utils.request_handlers import perform_post_request

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
