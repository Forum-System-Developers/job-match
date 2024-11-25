import logging
from uuid import UUID

from fastapi import status
from sqlalchemy.orm import Session

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.common import FilterParams
from app.schemas.job_ad import BaseJobAd
from app.schemas.job_application import MatchResponseRequest
from app.sql_app.job_ad.job_ad_status import JobAdStatus
from app.sql_app.job_application.job_application_status import JobStatus
from app.sql_app.match.match import Match, MatchStatus
from app.sql_app.professional.professional import ProfessionalStatus
from app.utils.processors import process_db_transaction

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
            case MatchStatus.REQUESTED_BY_JOB_APP:
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

    def _handle_create():
        match_request = Match(
            job_ad_id=job_ad_id,
            job_application_id=job_application_id,
            status=MatchStatus(MatchStatus.REQUESTED_BY_JOB_AD),
        )
        logger.info(
            f"Match created for JobApplication id{job_application_id} and JobAd id {job_ad_id} with status {MatchStatus.REQUESTED_BY_JOB_AD}"
        )
        db.add(match_request)
        db.commit()
        db.refresh(match_request)

        logger.info(
            f"Match for JobApplication id{job_application_id} and JobAd id {job_ad_id} added to the database"
        )
        return {"msg": "Match Request successfully sent"}

    return process_db_transaction(transaction_func=_handle_create, db=db)


def _get_match(job_application_id: UUID, job_ad_id: UUID, db: Session) -> Match | None:
    """
    Fetch Match instance.

    Args:
        job_application_id (UUID): The identifier of the Job Application.
        job_ad_id (UUID): The identifier of the Job Ad.
        db (Session): Database dependency.

    Returns:
        Optional[Match]: An existing entity or None.

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
    job_application_id: UUID,
    job_ad_id: UUID,
    accept_request: MatchResponseRequest,
    db: Session,
) -> dict:
    """
    Accepts or Rejects a Match request for a Job Application from a Company.

    Args:
        job_application_id (UUID): The identifier of the Job Application.
        job_ad_id (UUID): The identifier of the Job Ad.
        accept_request (MatchResponseRequest): Accept or reject a Match request.
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

    if accept_request.accept_request:
        return accept_match_request(
            match=existing_match,
            db=db,
            job_application_id=job_application_id,
            job_ad_id=job_ad_id,
        )

    else:
        return reject_match_request(
            match=existing_match,
            db=db,
            job_application_id=job_application_id,
            job_ad_id=job_ad_id,
        )


def reject_match_request(
    match: Match, db: Session, job_application_id: UUID, job_ad_id: UUID
) -> dict:
    def _handle_reject():
        match.status = MatchStatus.REJECTED
        db.commit()
        logger.info(
            f"Updated status for Match with JobAplication with id {job_application_id}, JobAd id {job_ad_id}"
        )
        return {"msg": "Match Request rejected"}

    return process_db_transaction(transaction_func=_handle_reject, db=db)


def accept_match_request(
    match: Match, db: Session, job_application_id: UUID, job_ad_id: UUID
) -> dict:
    """
    Updates .

    Args:
        match (MATCH): The Match instance.
        db (Session): Database dependency.

    Returns:
        dict: Confirmation message.

    """
    match_job_application = match.job_application
    professional = match_job_application.professional

    def _handle_accept():
        match.status = MatchStatus.ACCEPTED
        professional.status = ProfessionalStatus.BUSY
        professional.active_application_count -= 1
        match_job_application.status = JobStatus.MATCHED
        match.job_ad.status = JobAdStatus.ARCHIVED

        db.commit()
        logger.info(
            f"Updated statuses for JobAplication with id {job_application_id}, JobAd id {job_ad_id}, Professional with id {professional.id}"
        )
        return {"msg": "Match Request accepted"}

    return process_db_transaction(transaction_func=_handle_accept, db=db)


def get_match_requests_for_job_application(
    job_application_id: UUID, db: Session, filter_params: FilterParams
) -> list[BaseJobAd]:
    """
    Fetch match requests for the given Job Application.

    Args:
        job_application_id (UUID): The identifier of the Job Application.
        db (Session): Database dependency.
        filter_params (FilterParams): Filtering options for pagination.

    Returns:
        list[BaseJobAd]: Response models containing basic information for the Job Ads that sent the match request.
    """

    requests = (
        db.query(Match)
        .filter(
            Match.job_application_id == job_application_id,
            Match.status == MatchStatus.REQUESTED_BY_JOB_AD,
        )
        .offset(filter_params.offset)
        .limit(filter_params.limit)
        .all()
    )

    job_ads = [request.job_ad for request in requests]

    return [
        BaseJobAd(
            title=job_ad.title,
            description=job_ad.description,
            category_id=job_ad.category.id,
            location_id=job_ad.location.id,
            min_salary=job_ad.min_salary,
            max_salary=job_ad.max_salary,
        )
        for job_ad in job_ads
    ]
