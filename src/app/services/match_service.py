import logging
from uuid import UUID

from fastapi import status
from sqlalchemy.orm import Session

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.job_ad import JobAdResponse
from app.sql_app.job_ad.job_ad_status import JobAdStatus
from app.sql_app.job_application.job_application_status import JobStatus
from app.sql_app.match.match import Match, MatchStatus
from app.sql_app.professional.professional import ProfessionalStatus

logger = logging.getLogger(__name__)


def create_if_not_exists(
    job_application_id: UUID, job_ad_id: UUID, db: Session
) -> dict:
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
                raise ApplicationError(
                    detail="Match Request already sent",
                    status_code=status.HTTP_403_FORBIDDEN,
                )
            case MatchStatus.ACCEPTED:
                raise ApplicationError(
                    detail="Match Request already accepted",
                    status_code=status.HTTP_403_FORBIDDEN,
                )
            case MatchStatus.REJECTED:
                raise ApplicationError(
                    detail="Match Request was rejested, cannot create a new Match request",
                    status_code=status.HTTP_403_FORBIDDEN,
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


def _get_match(job_application_id: UUID, job_ad_id: UUID, db: Session) -> Match | None:
    """
    Fetch Match instance.

    Args:
        job_application_id (UUID): The identifier of the Job Application.
        job_ad_id (UUID): The identifier of the Job Ad.
        db (Session): Database dependency.

    Returns:
        Match | None: An existing entity or None.

    """
    match = (
        db.query(Match)
        .filter(
            Match.job_ad_id == job_ad_id, Match.job_application_id == job_application_id
        )
        .first()
    )
    return match


def process_request_from_company(
    job_application_id: UUID, job_ad_id: UUID, accept_request: bool, db: Session
):
    """
    Accepts or Rejects a Match request for a Job Application from a Company.

    Args:
        job_application_id (UUID): The identifier of the Job Application.
        job_ad_id (UUID): The identifier of the Job Ad.
        accept_request (bool): Accept or reject a Match request.
        db (Session): Database dependency.

    Raises:
        ApplicationError: If there is no existing Match.

    Returns:
        dict: A dictionary containing a success message if the match request is accepted or rejected.

    """
    existing_match = _get_match(
        job_application_id=job_application_id, job_ad_id=job_ad_id, db=db
    )
    if existing_match is None:
        logger.error(
            f"No existing Match for JobApplication id{job_application_id} and JobAd id {job_ad_id}"
        )
        raise ApplicationError(
            detail=f"No match found for JobApplication id{job_application_id} and JobAd id {job_ad_id}",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    if accept_request:
        existing_match.status = MatchStatus.ACCEPTED
        existing_match.job_application.professional.status = ProfessionalStatus.BUSY
        existing_match.job_application.status = JobStatus.MATCHED
        existing_match.job_ad.status = JobAdStatus.ARCHIVED

        logger.info(
            f"Updated statuses for JobAplication with id {job_application_id}, JobAd id {job_ad_id}, Professional with id {existing_match.job_application.professional.id}"
        )
        return {"msg": "Match Request accepted"}

    existing_match.status = MatchStatus.REJECTED
    logger.info(
        f"Updated status for Match with JobAplication with id {job_application_id}, JobAd id {job_ad_id}"
    )
    return {"msg": "Match Request rejected"}


def get_match_requests_for_job_application(
    job_application_id: UUID, db: Session
) -> list[JobAdResponse]:
    requests = (
        db.query(Match)
        .filter(
            Match.job_application_id == job_application_id,
            Match.status == MatchStatus.REQUESTED,
        )
        .all()
    )

    job_ads = [request.job_ad for request in requests]

    return [
        JobAdResponse.model_validate(job_ad, from_attributes=True) for job_ad in job_ads
    ]
