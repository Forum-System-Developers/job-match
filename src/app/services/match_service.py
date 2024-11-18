import logging
from uuid import UUID

from fastapi import status
from sqlalchemy.orm import Session
from sqlalchemy.orm.query import RowReturningQuery

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.address import CityResponse
from app.schemas.common import FilterParams, SearchParams
from app.schemas.job_application import (
    JobAplicationBase,
    JobApplicationResponse,
    JobSearchStatus,
)
from app.schemas.job_application import JobStatus as JobStatusInput
from app.schemas.professional import ProfessionalResponse
from app.schemas.skill import SkillBase
from app.schemas.user import UserResponse
from app.services import (
    city_service,
    professional_service,
    skill_service,
    job_ad_service,
)
from app.sql_app.match.match import Match, MatchStatus
from app.sql_app.job_application.job_application import JobApplication
from app.sql_app.job_application.job_application_status import JobStatus
from app.sql_app.job_application_skill.job_application_skill import JobApplicationSkill
from app.sql_app.professional.professional import Professional
from app.sql_app.skill.skill import Skill

logger = logging.getLogger(__name__)


def create_if_not_exists(
    job_application_id: UUID, job_ad_id: UUID, db: Session
) -> MatchStatus:
    existing_match = _get_match(
        job_application_id=job_application_id, job_ad_id=job_ad_id, db=db
    )
    if existing_match is not None:
        return existing_match.status

    match_request = Match(
        job_ad_id=job_ad_id,
        job_application_id=job_application_id,
        status=MatchStatus.REQUESTED,
    )
    logger.info(
        f"Match created for JobApplication id{job_application_id} and JobAd id {job_ad_id}"
    )
    db.add(match_request)
    db.commit()
    db.refresh(match_request)

    logger.info(
        f"Match for JobApplication id{job_application_id} and JobAd id {job_ad_id} added to the database"
    )

    return match_request.status


def _get_match(job_application_id: UUID, job_ad_id: UUID, db: Session) -> Match:
    match = (
        db.query(Match)
        .filter(
            Match.job_ad_id == job_ad_id, Match.job_application_id == job_application_id
        )
        .first()
    )
    return match
