import logging
from uuid import UUID

from fastapi import status

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.common import FilterParams, MessageResponse
from app.schemas.job_application import MatchResponseRequest
from app.schemas.match import (
    MatchRequestAd,
    MatchRequestApplication,
    MatchRequestCreate,
    MatchResponse,
)
from app.services.enums.match_status import MatchStatus
from app.services.external_db_service_urls import (
    MATCH_REQUESTS_BY_ID_URL,
    MATCH_REQUESTS_COMPANIES_URL,
    MATCH_REQUESTS_JOB_ADS_RECEIVED_URL,
    MATCH_REQUESTS_JOB_ADS_SENT_URL,
    MATCH_REQUESTS_JOB_APPLICATIONS_URL,
    MATCH_REQUESTS_PROFESSIONALS_URL,
    MATCH_REQUESTS_URL,
)
from app.services.utils.common import get_match_request_by_id
from app.services.utils.validators import (
    ensure_no_match_request,
    ensure_valid_job_ad_id,
    ensure_valid_job_application_id,
)
from app.utils.request_handlers import (
    perform_get_request,
    perform_patch_request,
    perform_post_request,
    perform_put_request,
)

logger = logging.getLogger(__name__)


def create_if_not_exists(job_application_id: UUID, job_ad_id: UUID) -> MessageResponse:
    """
    Creates a Match request for a Job Application from a Company.

    Args:
        job_application_id (UUID): The identifier of the Job Application.
        job_ad_id (UUID): The identifier of the Job Ad.

    Raises:
        ApplicationError: If there is an existing Match already

    Returns:
        MessageResponse: A message response indicating the success of the operation.

    """
    existing_match = get_match_request_by_id(
        job_ad_id=job_ad_id, job_application_id=job_application_id
    )
    if existing_match is not None:
        match existing_match.status:
            case MatchStatus.REQUESTED_BY_JOB_APP:
                raise ApplicationError(
                    detail="Match Request already sent",
                    status_code=status.HTTP_403_FORBIDDEN,
                )
            case MatchStatus.REQUESTED_BY_JOB_AD:
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
    match_create = MatchRequestCreate(
        job_ad_id=job_ad_id,
        job_application_id=job_application_id,
        status=MatchStatus.REQUESTED_BY_JOB_AD,
    )
    perform_post_request(
        url=MATCH_REQUESTS_URL,
        json={**match_create.model_dump(mode="json")},
    )
    logger.info(
        f"Match created for JobApplication id{job_application_id} and JobAd id {job_ad_id} with status {MatchStatus.REQUESTED_BY_JOB_AD}"
    )

    return MessageResponse(message="Match Request successfully sent")


def process_request_from_company(
    job_application_id: UUID,
    job_ad_id: UUID,
    accept_request: MatchResponseRequest,
) -> MessageResponse:
    """
    Accepts or Rejects a Match request for a Job Application from a Company.

    Args:
        job_application_id (UUID): The identifier of the Job Application.
        job_ad_id (UUID): The identifier of the Job Ad.
        accept_request (MatchResponseRequest): Accept or reject a Match request.

    Raises:
        ApplicationError: If there is no existing Match.

    Returns:
        MessageResponse: A message response indicating the success of the operation.

    """
    existing_match = get_match_request_by_id(
        job_ad_id=job_ad_id,
        job_application_id=job_application_id,
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
            job_application_id=job_application_id,
            job_ad_id=job_ad_id,
        )

    else:
        return reject_match_request(
            job_application_id=job_application_id,
            job_ad_id=job_ad_id,
        )


def reject_match_request(
    job_ad_id: UUID,
    job_application_id: UUID,
) -> MessageResponse:
    perform_patch_request(
        url=MATCH_REQUESTS_BY_ID_URL.format(
            job_ad_id=job_ad_id, job_application_id=job_application_id
        ),
        json={"status": MatchStatus.REJECTED},
    )
    logger.info(
        f"Match Request rejected for JobApplication id{job_application_id} and JobAd id {job_ad_id}"
    )

    return MessageResponse(message="Match Request rejected")


def accept_match_request(
    job_application_id: UUID,
    job_ad_id: UUID,
) -> MessageResponse:
    """
    Accepts a match request for a given job application and job advertisement.

    Args:
        job_application_id (UUID): The unique identifier of the job application.
        job_ad_id (UUID): The unique identifier of the job advertisement.

    Returns:
        MessageResponse: A response object containing a message indicating the match request was accepted.
    """
    perform_put_request(
        url=MATCH_REQUESTS_BY_ID_URL.format(
            job_ad_id=job_ad_id, job_application_id=job_application_id
        ),
    )
    logger.info(
        f"Match Request accepted for JobApplication id{job_application_id} and JobAd id {job_ad_id}"
    )

    return MessageResponse(message="Match Request accepted")


def get_match_requests_for_job_application(
    job_application_id: UUID,
    filter_params: FilterParams,
) -> list[MatchRequestAd]:
    """
    Fetch match requests for the given Job Application.

    Args:
        job_application_id (UUID): The identifier of the Job Application.
        filter_params (FilterParams): Filtering options for pagination.

    Returns:
        list[MatchRequestAd]: Response models containing basic information for the Job Ads that sent the match request.
    """

    requests = perform_get_request(
        url=MATCH_REQUESTS_JOB_APPLICATIONS_URL.format(
            job_application_id=job_application_id
        ),
        params=filter_params.model_dump(),
    )

    return [MatchRequestAd(**request) for request in requests]


def get_match_requests_for_professional(
    professional_id: UUID,
) -> list[MatchRequestAd]:
    requests = perform_get_request(
        url=MATCH_REQUESTS_PROFESSIONALS_URL.format(professional_id=professional_id)
    )

    return [MatchRequestAd(**request) for request in requests]


def accept_job_application_match_request(
    job_ad_id: UUID,
    job_application_id: UUID,
    company_id: UUID,
) -> MessageResponse:
    """
    Accepts a match request between a job advertisement and a job application.

    This function ensures that the provided job advertisement ID and job application ID
    are valid, and that there is a valid match request between them. It then updates the
    statuses of the job advertisement, job application, and match request accordingly,
    commits the changes to the database, and logs the operation.

    Args:
        job_ad_id (UUID): The unique identifier of the job advertisement.
        job_application_id (UUID): The unique identifier of the job application.

    Returns:
        AcceptRequestMatchResponse: The response indicating successful match acceptance.
    """
    ensure_valid_job_ad_id(job_ad_id=job_ad_id, company_id=company_id)

    return accept_match_request(
        job_ad_id=job_ad_id,
        job_application_id=job_application_id,
    )


def send_job_ad_match_request(
    job_ad_id: UUID,
    job_application_id: UUID,
) -> MessageResponse:
    """
    Sends a match request from a job application to job advertisement.

    Args:
        job_ad_id (UUID): The unique identifier of the job advertisement.
        job_application_id (UUID): The unique identifier of the job application.

    Returns:
        MessageResponse: A response object containing a message indicating the result of the operation.
    """
    ensure_valid_job_ad_id(job_ad_id=job_ad_id)
    ensure_valid_job_application_id(job_application_id=job_application_id)
    ensure_no_match_request(
        job_ad_id=job_ad_id,
        job_application_id=job_application_id,
    )

    perform_post_request(
        url=MATCH_REQUESTS_URL,
        json=MatchRequestCreate(
            job_ad_id=job_ad_id,
            job_application_id=job_application_id,
            status=MatchStatus.REQUESTED_BY_JOB_APP,
        ).model_dump(mode="json"),
    )
    logger.info(
        f"Sent match request from job ad with id {job_ad_id} to job application with id {job_application_id}"
    )

    return MessageResponse(message="Match request sent")


def view_received_job_ad_match_requests(
    job_ad_id: UUID,
    company_id: UUID,
) -> list[MatchResponse]:
    """
    Retrieve match requests for a given job advertisement.

    Args:
        job_ad_id (UUID): The unique identifier of the job advertisement.
        company_id (UUID): The unique identifier of the company.

    Returns:
        list[MatchResponse]: A list of match responses for the specified job advertisement.
    """
    ensure_valid_job_ad_id(job_ad_id=job_ad_id, company_id=company_id)
    requests = perform_get_request(
        url=MATCH_REQUESTS_JOB_ADS_RECEIVED_URL.format(job_ad_id=job_ad_id),
    )
    logger.info(f"Retrieved {len(requests)} requests for job ad with id {job_ad_id}")

    return [MatchResponse(**request) for request in requests]


def view_sent_job_application_match_requests(
    job_ad_id: UUID,
    company_id: UUID,
) -> list[MatchResponse]:
    """
    Retrieve sent match requests for a given job advertisement.

    Args:
        job_ad_id (UUID): The unique identifier of the job advertisement.

    Returns:
        list[MatchResponse]: A list of match responses for the specified job advertisement.
    """
    ensure_valid_job_ad_id(job_ad_id=job_ad_id, company_id=company_id)
    requests = perform_get_request(
        url=MATCH_REQUESTS_JOB_ADS_SENT_URL.format(job_ad_id=job_ad_id),
    )
    logger.info(
        f"Retrieved {len(requests)} sent requests for job ad with id {job_ad_id}"
    )

    return [MatchResponse(**request) for request in requests]


def get_company_match_requests(
    company_id: UUID,
    filter_params: FilterParams,
) -> list[MatchRequestApplication]:
    """
    Retrieve match requests for a given company.

    Args:
        company_id (UUID): The unique identifier of the company.

    Returns:
        list[MatchRequestApplication]: A list of match responses for the specified company.
    """
    requests = perform_get_request(
        url=MATCH_REQUESTS_COMPANIES_URL.format(company_id=company_id),
        params=filter_params.model_dump(),
    )
    logger.info(f"Retrieved {len(requests)} requests for company with id {company_id}")

    return [MatchRequestApplication(**request) for request in requests]
