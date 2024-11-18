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
from app.sql_app.job_ad.job_ad_status import JobAdStatus
from app.sql_app.job_application.job_application_status import JobStatus
from app.sql_app.job_application_skill.job_application_skill import JobApplicationSkill
from app.sql_app.professional.professional import ProfessionalStatus
from app.sql_app.skill.skill import Skill

logger = logging.getLogger(__name__)


def create_if_not_exists(
    job_application_id: UUID, job_ad_id: UUID, db: Session
) -> MatchStatus:
    """
    Creates a Match request for a Job Application from a Company.

    Args:
        job_application_id (UUID): The identifier of the Job Application.
        job_ad_id (UUID): The identifier of the Job Ad.
        db (Session): Database dependency.

    Raises:
        ApplicationError: If there is an existing Match already

    Returns:
        dict: A dictionary containing a success message if the match request is created successfully.

    """
    existing_match = _get_match(
        job_application_id=job_application_id, job_ad_id=job_ad_id, db=db
    )
    if existing_match is not None:
        match existing_match.status:
            case MatchStatus.REQUESTED:
                raise ApplicationError(detail="Match Request already sent")
            case MatchStatus.ACCEPTED:
                raise ApplicationError(detail="Match Request already accepted")
            case MatchStatus.REJECTED:
                raise ApplicationError(
                    detail="Match Request was rejested, cannot create a new Match request"
                )

    match_request = Match(
        job_ad_id=job_ad_id,
        job_application_id=job_application_id,
        status=MatchStatus.REQUESTED,
    )
    logger.info(
        f"Match created for JobApplication id{job_application_id} and JobAd id {job_ad_id} with status {MatchStatus.REQUESTED}"
    )
    db.add(match_request)
    db.commit()
    db.refresh(match_request)

    logger.info(
        f"Match for JobApplication id{job_application_id} and JobAd id {job_ad_id} added to the database"
    )

    return {"msg": "Match Request successfully sent"}


def _get_match(job_application_id: UUID, job_ad_id: UUID, db: Session) -> Match:
    match = (
        db.query(Match)
        .filter(
            Match.job_ad_id == job_ad_id, Match.job_application_id == job_application_id
        )
        .first()
    )
    return match


def accept_request_from_company(job_application_id: UUID, job_ad_id: UUID, db: Session):
    """
    Accepts a Match request for a Job Application from a Company.

    Args:
        job_application_id (UUID): The identifier of the Job Application.
        job_ad_id (UUID): The identifier of the Job Ad.
        db (Session): Database dependency.

    Raises:
        ApplicationError: If there is no existing Match.

    Returns:
        dict: A dictionary containing a success message if the match request is accepted successfully.

    """
    existing_match = _get_match(
        job_application_id=job_application_id, job_ad_id=job_ad_id, db=db
    )
    if existing_match is None:
        raise ApplicationError(
            detail=f"No match found for JobApplication id{job_application_id} and JobAd id {job_ad_id}"
        )

    existing_match.status = MatchStatus.ACCEPTED
    existing_match.job_application.professional.status = ProfessionalStatus.BUSY
    existing_match.job_application.status = JobStatus.MATCHED
    existing_match.job_ad.status = JobAdStatus.ARCHIVED

    return {"msg": "Match Request accepted"}
