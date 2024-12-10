import io
import logging
from uuid import UUID

from fastapi import UploadFile, status
from fastapi.responses import StreamingResponse
from requests import Response

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.common import FilterParams, MessageResponse, SearchParams
from app.schemas.job_application import JobApplicationResponse, JobSearchStatus
from app.schemas.match import MatchRequestAd
from app.schemas.professional import (
    PrivateMatches,
    ProfessionalCreate,
    ProfessionalCreateFinal,
    ProfessionalRequestBody,
    ProfessionalResponse,
    ProfessionalUpdate,
    ProfessionalUpdateFinal,
    ProfessionalUpdateRequestBody,
)
from app.schemas.skill import SkillResponse
from app.schemas.user import User
from app.services import city_service, match_service
from app.services.external_db_service_urls import (
    PROFESSIONAL_BY_USERNAME_URL,
    PROFESSIONALS_BY_ID_URL,
    PROFESSIONALS_CV_URL,
    PROFESSIONALS_JOB_APPLICATIONS_URL,
    PROFESSIONALS_PHOTO_URL,
    PROFESSIONALS_SKILLS_URL,
    PROFESSIONALS_TOGGLE_STATUS_URL,
    PROFESSIONALS_URL,
)
from app.services.utils.common import get_professional_by_id
from app.services.utils.file_utils import validate_uploaded_cv, validate_uploaded_file
from app.services.utils.validators import is_unique_email, is_unique_username
from app.utils.password_utils import hash_password
from app.utils.request_handlers import (
    perform_delete_request,
    perform_get_request,
    perform_patch_request,
    perform_post_request,
    perform_put_request,
)

logger = logging.getLogger(__name__)


def create(professional_request: ProfessionalRequestBody) -> ProfessionalResponse:
    """
    Creates an instance of the Professional model.

    Args:
        professional_request (ProfessionalRequestBody): Pydantic schema for collecting data.

    Returns:
        Professional: Pydantic response model for Professional.
    """
    professional_data = professional_request.professional
    _validate_unique_professional_details(professional_create=professional_data)
    city = city_service.get_by_name(city_name=professional_data.city)

    hashed_password = hash_password(password=professional_data.password)

    professional_create_data = ProfessionalCreateFinal(
        **professional_data.model_dump(exclude={"city", "password"}, mode="json"),
        city_id=city.id,
        password_hash=hashed_password,
    )

    professional = perform_post_request(
        url=PROFESSIONALS_URL,
        json={
            **professional_create_data.model_dump(mode="json"),
        },
    )
    logger.info(f"Professional with id {professional['id']} created")

    return ProfessionalResponse(**professional)


def update(
    professional_id: UUID,
    professional_request: ProfessionalUpdateRequestBody,
) -> ProfessionalResponse:
    """
    Update the professional's information.

    Args:
        professional_id (UUID): The unique identifier of the professional.
        professional_data (ProfessionalUpdate): The data to update the professional with.

    Returns:
        ProfessionalResponse: The updated professional information.
    """
    professional_data = professional_request.professional
    professional_update_data = ProfessionalUpdateFinal(
        **professional_data.model_dump(exclude={"city"}, mode="json"),
        status=professional_request.status,
    )
    if professional_data.city is not None:
        city = city_service.get_by_name(city_name=professional_data.city)
        professional_update_data.city_id = city.id

    professional = perform_put_request(
        url=PROFESSIONALS_BY_ID_URL.format(professional_id=professional_id),
        json={
            **professional_update_data.model_dump(mode="json"),
        },
    )
    logger.info(f"Professional with id {professional_id} updated successfully")

    return ProfessionalResponse(**professional)


def upload_photo(professional_id: UUID, photo: UploadFile) -> MessageResponse:
    """
    Uploads a photo for a professional.

    Args:
        professional_id (UUID): The unique identifier of the professional.
        photo (UploadFile): The photo file to be uploaded.

    Returns:
        MessageResponse: A response message indicating the result of the upload operation.
    """
    validate_uploaded_file(photo)
    perform_post_request(
        url=PROFESSIONALS_PHOTO_URL.format(professional_id=professional_id),
        files={"photo": (photo.filename, photo.file, photo.content_type)},
    )
    logger.info(f"Uploaded photo for professional with id {professional_id}")

    return MessageResponse(message="Photo uploaded successfully")


def upload_cv(professional_id: UUID, cv: UploadFile) -> MessageResponse:
    """
    Uploads a CV for a professional.

    Args:
        professional_id (UUID): The unique identifier of the professional.
        cv (UploadFile): The CV file to be uploaded.

    Returns:
        MessageResponse: A response message indicating the result of the upload.
    """
    validate_uploaded_cv(cv)
    perform_post_request(
        url=PROFESSIONALS_CV_URL.format(professional_id=professional_id),
        files={"cv": (cv.filename, cv.file, cv.content_type)},
    )
    logger.info(f"Uploaded CV for professional with id {professional_id}")

    return MessageResponse(message="CV uploaded successfully")


def download_photo(professional_id: UUID) -> StreamingResponse:
    """
    Downloads the photo of a professional given their ID.

    Args:
        professional_id (UUID): The unique identifier of the professional.

    Returns:
        StreamingResponse: A streaming response containing the photo in PNG format.
    """
    response = perform_get_request(
        url=PROFESSIONALS_PHOTO_URL.format(professional_id=professional_id)
    )
    logger.info(f"Downloaded photo of professional with id {professional_id}")

    return StreamingResponse(io.BytesIO(response.content), media_type="image/png")


def download_cv(professional_id: UUID) -> StreamingResponse:
    """
    Downloads the CV of a professional by their ID.

    Args:
        professional_id (UUID): The unique identifier of the professional.

    Returns:
        StreamingResponse: A streaming response containing the professional's CV.
    """
    response = perform_get_request(
        url=PROFESSIONALS_CV_URL.format(professional_id=professional_id)
    )
    logger.info(f"Downloaded CV of professional with id {professional_id}")

    return _create_cv_streaming_response(response)


def delete_cv(professional_id: UUID) -> MessageResponse:
    """
    Deletes the CV of a professional given their ID.

    Args:
        professional_id (UUID): The unique identifier of the professional whose CV is to be deleted.

    Returns:
        MessageResponse: A response object containing a message indicating the result of the operation.
    """
    perform_delete_request(
        url=PROFESSIONALS_CV_URL.format(professional_id=professional_id)
    )
    logger.info(f"Deleted CV of professional with id {professional_id}")

    return MessageResponse(message="CV deleted successfully")


def get_by_id(professional_id: UUID) -> ProfessionalResponse:
    """
    Retrieve a Professional profile by its ID.

    Args:
        professional_id (UUID): The identifier of the professional.

    Returns:
        ProfessionalResponse: The created professional profile response.
    """
    professional = perform_get_request(
        url=PROFESSIONALS_BY_ID_URL.format(professional_id=professional_id)
    )
    logger.info(f"Retrieved professional with id {professional_id}")

    return ProfessionalResponse(**professional)


def get_all(
    filter_params: FilterParams,
    search_params: SearchParams,
) -> list[ProfessionalResponse]:
    """
    Retrieve all Professional profiles.

    Args:
        filer_params (FilterParams): Pydantic schema for filtering params.
        search_params (SearchParams): Search parameter for limiting search results.
    Returns:
        list[ProfessionalResponse]: A list of Professional Profiles that are visible for Companies.
    """
    params = {
        **search_params.model_dump(mode="json"),
        **filter_params.model_dump(mode="json"),
    }
    professionals = perform_get_request(
        url=PROFESSIONALS_URL,
        params=params,
    )
    logger.info(f"Retrieved {len(professionals)} professionals")

    return [ProfessionalResponse(**professional) for professional in professionals]


def _get_by_id(professional_id: UUID) -> ProfessionalResponse:
    """
    Retrieves an instance of the Professional model or None.

    Args:
        professional_id (UUID): The identifier of the Professional.

    Returns:
        Professional: SQLAlchemy model for Professional.

    Raises:
        ApplicationError: If the professional with the given id is
            not found in the database.
    """
    professional = get_professional_by_id(professional_id=professional_id)
    if professional is None:
        logger.error(f"Professional with id {professional_id} not found")
        raise ApplicationError(
            detail=f"Professional with id {professional_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    logger.info(f"Professional with id {professional_id} fetched")

    return professional


def set_matches_status(
    professional_id: UUID,
    private_matches: PrivateMatches,
) -> MessageResponse:
    perform_patch_request(
        url=PROFESSIONALS_TOGGLE_STATUS_URL.format(professional_id=professional_id),
        json={**private_matches.model_dump(mode="json")},
    )

    return MessageResponse(
        message=f"Matches set as {'private' if private_matches.status else 'public'}"
    )


def get_by_username(username: str) -> User:
    """
    Fetch a Professional by their username.

    Args:
        username (str): The username of the Professional

    Raises:
        ApplicationError: When username does not exist.

    Returns:
        User (User): Pydantic DTO containing User information.

    """
    professional = perform_get_request(
        url=PROFESSIONAL_BY_USERNAME_URL.format(username=username)
    )
    logger.info(f"Retrieved professional with username {username}")

    return User(
        id=professional.id,
        username=professional.username,
        password=professional.password,
    )


def get_applications(
    professional_id: UUID,
    # current_user: ProfessionalResponse | CompanyResponse,
    application_status: JobSearchStatus,
    filter_params: FilterParams,
) -> list[JobApplicationResponse]:
    """
    Get a list of all JobApplications for a Professional with the given ID.

    Args:
        professional_id (UUID): The identifier of the Professional.

    Returns:
        list[JobApplicationResponse]: List of Job Applications Pydantic models.
    """
    job_applications = perform_get_request(
        url=PROFESSIONALS_JOB_APPLICATIONS_URL.format(professional_id=professional_id),
        params={
            **filter_params.model_dump(mode="json"),
            "application_status": application_status.value,
        },
    )

    return [
        JobApplicationResponse(**job_application)
        for job_application in job_applications
    ]


def get_skills(professional_id: UUID) -> list[SkillResponse]:
    """
    Fetch skillset for professional.

    Args:
        professional_id (UUID): The identifier of the professional.
    """
    skills = perform_get_request(
        url=PROFESSIONALS_SKILLS_URL.format(professional_id=professional_id)
    )
    logger.info(f"Retrieved skills for professional with id {professional_id}")

    return [SkillResponse(**skill) for skill in skills]


def get_match_requests(professional_id: UUID) -> list[MatchRequestAd]:
    """
    Fetches Match Requests for the given Professional.

    Args:
        professional_id (UUID): The identifier of the Professional.

    Returns:
        list[MatchRequest]: List of Pydantic models containing basic information about the match request.
    """
    professional = _get_by_id(professional_id=professional_id)

    match_requests = match_service.get_match_requests_for_professional(
        professional_id=professional.id
    )

    return match_requests


def _create_cv_streaming_response(response: Response) -> StreamingResponse:
    """
    Create a StreamingResponse from the given response, including specific headers.

    Args:
        response: The response object containing the content and headers.

    Returns:
        StreamingResponse: The streaming response with the appropriate headers.
    """
    streaming_response = StreamingResponse(
        io.BytesIO(response.content), media_type="application/pdf"
    )
    streaming_response.headers["Content-Disposition"] = response.headers[
        "Content-Disposition"
    ]
    streaming_response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"

    return streaming_response


def _validate_unique_professional_details(
    professional_create: ProfessionalCreate,
) -> None:
    """
    Check if the username and email provided for creating a Professional are unique.

    Args:
        professional_create (ProfessionalCreate): The data for creating a Professional.

    Raises:
        ApplicationError: If the username or email is already taken.
    """
    if not is_unique_username(username=professional_create.username):
        raise ApplicationError(
            detail="Username already taken", status_code=status.HTTP_409_CONFLICT
        )
    if not is_unique_email(email=professional_create.email):
        raise ApplicationError(
            detail="Email already taken", status_code=status.HTTP_409_CONFLICT
        )
