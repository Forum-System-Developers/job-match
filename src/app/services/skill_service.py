import logging

from app.schemas.skill import Skill, SkillCreate, SkillResponse
from app.services.enums.skill_level import SkillLevel
from app.services.utils.common import get_skill_by_id
from app.sql_app.job_ad_skill.job_ad_skill import JobAdSkill
from app.sql_app.job_application_skill.job_application_skill import JobApplicationSkill
from app.sql_app.pending_skill.pending_skill import PendingSkill
from app.sql_app.skill.skill import Skill
from app.utils.request_handlers import perform_post_request
from tests.services.urls import SKILLS_URL

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
