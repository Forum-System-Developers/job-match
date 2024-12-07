import io
import logging
from datetime import datetime
from uuid import UUID

from fastapi import UploadFile, status
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session, joinedload

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.common import FilterParams, MessageResponse, SearchParams
from app.schemas.job_ad import JobAdPreview
from app.schemas.job_application import JobApplicationResponse, JobSearchStatus
from app.schemas.match import MatchRequestAd
from app.schemas.professional import (
    PrivateMatches,
    ProfessionalCreate,
    ProfessionalRequestBody,
    ProfessionalResponse,
    ProfessionalUpdateRequestBody,
)
from app.schemas.skill import SkillResponse
from app.schemas.user import User
from app.services import city_service, match_service
from app.services.enums.job_application_status import JobStatus
from app.services.utils.file_utils import handle_file_upload
from app.services.utils.validators import unique_email, unique_username
from app.sql_app.job_ad.job_ad import JobAd
from app.sql_app.job_application.job_application import JobApplication
from app.sql_app.job_application_skill.job_application_skill import JobApplicationSkill
from app.sql_app.match.match import Match
from app.sql_app.professional.professional import Professional
from app.sql_app.professional.professional_status import ProfessionalStatus
from app.utils.password_utils import hash_password
from app.utils.processors import process_db_transaction

logger = logging.getLogger(__name__)


def create(
    professional_request: ProfessionalRequestBody,
    db: Session,
) -> ProfessionalResponse:
    """
    Creates an instance of the Professional model.

    Args:
        professional_request (ProfessionalRequestBody): Pydantic schema for collecting data.
        db (Session): Database dependency.

    Returns:
        Professional: Pydantic response model for Professional.
    """
    professional_create = professional_request.professional
    professional_status = professional_request.status

    city = city_service.get_by_name(city_name=professional_create.city)
    if city is None:
        logger.error(f"City name {professional_create.city} not found")
        raise ApplicationError(
            detail=f"City with name {professional_create.city} was not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    logger.info(f"City {city} fetched")

    professional = _register_professional(
        professional_create=professional_create,
        professional_status=professional_status,
        city_id=city.id,
        db=db,
    )

    logger.info(f"Professional with id {professional.id} created")
    return ProfessionalResponse.create(professional=professional)


def update(
    professional_id: UUID,
    professional_request: ProfessionalUpdateRequestBody,
    db: Session,
) -> ProfessionalResponse:
    """
    Upates an instance of the Professional model.

    Args:
        professional_id (UUID): The identifier of the professional.
        professional_request (ProfessionalRequestBody): Pydantic schema for collecting data.
        db (Session): Database dependency.

    Returns:
        Professional: Professional Pydantic response model.

    Raises:
        ApplicationError: If the professional with the given id is
            not found in the database.
        ApplicationError: If the city with the given name is
            not found in the database.

    """
    professional = _get_by_id(professional_id=professional_id, db=db)

    professional = _update_attributes(
        professional_request=professional_request, professional=professional, db=db
    )

    matched_ads = (
        _get_matches(professional_id=professional_id, db=db)
        if not professional.has_private_matches
        else None
    )

    db.commit()
    db.refresh(professional)

    logger.info(f"Professional with id {professional.id} updated successfully")
    return ProfessionalResponse.create(
        professional=professional,
        matched_ads=matched_ads,
    )


def upload_photo(professional_id: UUID, photo: UploadFile, db: Session) -> dict:
    """
    Upload Professional photo to the database

    Args:
        professional_id (UUID): The identifier of the Professional.
        photo (UploadFile): The upload file.
        db (Session): Database dependency.

    Returns:
        dict: Confirmation message.
    """
    profesional = _get_by_id(professional_id=professional_id, db=db)

    def _handle_upload():
        upload_photo = handle_file_upload(file_to_upload=photo)
        profesional.photo = upload_photo
        profesional.updated_at = datetime.now()
        db.commit()
        return {"msg": "Photo successfully uploaded"}

    return process_db_transaction(transaction_func=_handle_upload, db=db)


def upload_cv(professional_id: UUID, cv: UploadFile, db: Session) -> dict:
    """
    Upload Professional photo to the database

    Args:
        professional_id (UUID): The identifier of the Professional.
        cv (UploadFile): The upload file.
        db (Session): Database dependency.

    Returns:
        dict: Confirmation message.
    """
    profesional = _get_by_id(professional_id=professional_id, db=db)

    def _handle_upload():
        if cv.content_type != "application/pdf":
            raise ApplicationError(
                detail="Only PDF files are allowed.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        upload_cv = handle_file_upload(file_to_upload=cv)
        profesional.cv = upload_cv
        profesional.updated_at = datetime.now()
        db.commit()
        return {"msg": "CV successfully uploaded"}

    return process_db_transaction(transaction_func=_handle_upload, db=db)


def download_photo(
    professional_id: UUID, db: Session
) -> StreamingResponse | JSONResponse:
    """
    Fetches the photo of the Professional with the given UUID.

    Args:
        professional_id (UUID): Identifier of the Professional.
        db (Session): Database dependency.

    Returns:
        bytes | dict:
    """
    professional = _get_by_id(professional_id=professional_id, db=db)
    photo = professional.photo
    if photo is None:
        return JSONResponse(content={"msg": "No available photo"})

    return StreamingResponse(io.BytesIO(photo), media_type="image/png")


def download_cv(professional_id: UUID, db: Session) -> StreamingResponse | JSONResponse:
    """
    Fetches the CV of the Professional with the given UUID.

    Args:
        professional_id (UUID): Identifier of the Professional.
        db (Session): Database dependency.

    Returns:
        bytes | dict:
    """
    professional = _get_by_id(professional_id=professional_id, db=db)
    cv = professional.cv
    if cv is None:
        return JSONResponse(content={"msg": "No available CV"})

    filename = f"{professional.first_name}_{professional.last_name}_CV.pdf"
    response = StreamingResponse(io.BytesIO(cv), media_type="application/pdf")
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"

    return response


def delete_cv(professional_id: UUID, db: Session) -> MessageResponse:
    """
    Deletes the CV of a professional by setting the CV attribute to None and updating the updated_at timestamp.

    Args:
        professional_id (UUID): The unique identifier of the professional whose CV is to be deleted.
        db (Session): The database session used to perform the operation.

    Returns:
        MessageResponse: A response object containing a success message.

    Raises:
        ApplicationError: If the professional's CV is not found.
    """
    professional = _get_by_id(professional_id=professional_id, db=db)
    if professional.cv is None:
        raise ApplicationError(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CV for Job Application with id {professional_id} not found",
        )
    professional.cv = None
    professional.updated_at = datetime.now()
    db.commit()
    logger.info(f"Deleted CV of professional with id {professional_id}")

    return MessageResponse(message="CV deleted successfully")


def get_by_id(professional_id: UUID, db: Session) -> ProfessionalResponse:
    """
    Retrieve a Professional profile by its ID.

    Args:
        professional_id (UUID): The identifier of the professional.
        db (Session): Database session dependency.

    Returns:
        ProfessionalResponse: The created professional profile response.
    """
    professional = _get_by_id(professional_id=professional_id, db=db)

    matched_ads = (
        _get_matches(professional_id=professional_id, db=db)
        if not professional.has_private_matches
        else None
    )

    return ProfessionalResponse.create(
        professional=professional, matched_ads=matched_ads
    )


def get_all(
    db: Session, filter_params: FilterParams, search_params: SearchParams
) -> list[ProfessionalResponse]:
    """
    Retrieve all Professional profiles.

    Args:
        db (Session): The database session.
        filer_params (FilterParams): Pydantic schema for filtering params.
        search_params (SearchParams): Search parameter for limiting search results.
    Returns:
        list[ProfessionalResponse]: A list of Professional Profiles that are visible for Companies.
    """

    query = (
        db.query(Professional)
        .options(
            joinedload(Professional.job_applications)
            .joinedload(JobApplication.skills)
            .joinedload(JobApplicationSkill.skill)
        )
        .filter(Professional.status == ProfessionalStatus.ACTIVE)
    )

    logger.info("Retreived all professional profiles that are with status ACTIVE")

    # if search_params.skills:
    #     query = query.filter(Skill.name.in_(search_params.skills))
    #     logger.info(f"Filtered Professionals by skills: {search_params.skills}")

    if search_params.order == "desc":
        query.order_by(getattr(Professional, search_params.order_by).desc())
    else:
        query.order_by(getattr(Professional, search_params.order_by).asc())
    logger.info(
        f"Order Professionals based on search params order {search_params.order} and order_by {search_params.order_by}"
    )

    result: list[Professional] = (
        query.offset(filter_params.offset).limit(filter_params.limit).all()
    )

    logger.info("Limited public topics based on offset and limit")

    return [
        ProfessionalResponse.create(professional=professional)
        for professional in result
    ]


def _get_by_id(professional_id: UUID, db: Session) -> Professional:
    """
    Retrieves an instance of the Professional model or None.

    Args:
        professional_id (UUID): The identifier of the Professional.
        db (Session): Database dependency.

    Returns:
        Professional: SQLAlchemy model for Professional.

    Raises:
        ApplicationError: If the professional with the given id is
            not found in the database.
    """
    professional = (
        db.query(Professional).filter(Professional.id == professional_id).first()
    )
    if professional is None:
        logger.error(f"Professional with id {professional_id} not found")
        raise ApplicationError(
            detail=f"Professional with id {professional_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    logger.info(f"Professional with id {professional_id} fetched")
    return professional


def _get_matches(professional_id: UUID, db: Session) -> list[JobAdPreview]:
    """
    Fetches Matched Job Ads for the given Professional.

    Args:
        professional (Professional): The existing professional object to be updated.
        db (Session): Database dependency.

    Returns:
        list[JobAdPreview]: List of Pydantic models containing basic information about the matched Job Ad.
    """
    ads: list[JobAd] = (
        db.query(JobAd)
        .join(Match, Match.job_ad_id == JobAd.id)
        .join(JobApplication, Match.job_application_id == JobApplication.id)
        .filter(
            JobApplication.professional_id == professional_id,
            JobApplication.status == JobStatus.MATCHED,
        )
        .all()
    )

    return [JobAdPreview.create(ad) for ad in ads]


def _update_attributes(
    professional_request: ProfessionalUpdateRequestBody,
    professional: Professional,
    db: Session,
) -> Professional:
    """
    Updates the attributes of a professional's profile based on the provided ProfessionalUpdate model.

    Args:
        professional_request (ProfessionalUpdateRequestBody): The updated information for the professional.
        professional (Professional): The existing professional object to be updated.
        db (Session): The database session used for querying or interacting with the database.

    Returns:
        Professional (Professional): The updated professional object with modified attributes.
    """
    professional_update = professional_request.professional
    professional_status = professional_request.status

    if professional.status != professional_status:
        professional.status = professional_status
        logger.info("Professional status updated successfully")

    if (
        professional_update.city is not None
    ) and professional_update.city != professional.city.name:
        city = city_service.get_by_name(city_name=professional_update.city)
        professional.city_id = city.id
        logger.info("professional city updated successfully")

    if (
        professional_update.description is not None
    ) and professional.description != professional_update.description:
        professional.description = professional_update.description
        logger.info("Professional description updated successfully")

    if (
        professional_update.first_name is not None
    ) and professional.first_name != professional_update.first_name:
        professional.first_name = professional_update.first_name
        logger.info("Professional first name updated successfully")

    if (
        professional_update.last_name is not None
    ) and professional.last_name != professional_update.last_name:
        professional.last_name = professional_update.last_name
        logger.info("Professional last name updated successfully")

    def _handle_update():
        db.commit()
        db.refresh(professional)
        logger.info(f"Professional {professional.id} updated successfully.")

        return professional

    return process_db_transaction(transaction_func=_handle_update, db=db)


def set_matches_status(
    professional_id: UUID, db: Session, private_matches: PrivateMatches
) -> dict:
    professional = _get_by_id(professional_id=professional_id, db=db)

    def _update_status():
        professional.has_private_matches = private_matches.status
        db.commit()

        return {
            "msg": f"Matches set as {'private' if private_matches.status else 'public'}"
        }

    return process_db_transaction(transaction_func=_update_status, db=db)


def get_by_username(username: str, db: Session) -> User:
    """
    Fetch a Professional by their username.

    Args:
        username (str): The username of the Professional
        db (Session): Database dependency

    Raises:
        ApplicationError: When username does not exist.

    Returns:
        User (User): Pydantic DTO containing User information.

    """

    professional = (
        db.query(Professional).filter(Professional.username == username).first()
    )
    if professional is None:
        raise ApplicationError(
            detail=f"User with username {username} does not exist",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return User(
        id=professional.id,
        username=professional.username,
        password=professional.password,
    )


def get_applications(
    professional_id: UUID,
    # current_user: ProfessionalResponse | CompanyResponse,
    db: Session,
    application_status: JobSearchStatus,
    filter_params: FilterParams,
) -> list[JobApplicationResponse]:
    """
    Get a list of all JobApplications for a Professional with the given ID.

    Args:
        professional_id (UUID): The identifier of the Professional.
        db (Session): Database dependency.

    Returns:
        list[JobApplicationResponse]: List of Job Applications Pydantic models.
    """
    professional = _get_by_id(professional_id=professional_id, db=db)
    if (
        professional.has_private_matches
        and application_status.value == JobSearchStatus.MATCHED
        # and isinstance(current_user, CompanyResponse)
    ):
        raise ApplicationError(
            detail="Professional has set their Matches to Private",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    search_status = JobStatus(application_status.value)

    applications = (
        db.query(JobApplication)
        .filter(
            JobApplication.professional_id == professional_id,
            JobApplication.status == search_status,
        )
        .offset(filter_params.offset)
        .limit(filter_params.limit)
        .all()
    )

    return [
        JobApplicationResponse.create(
            professional=professional, job_application=application, db=db
        )
        for application in applications
    ]


def _register_professional(
    professional_create: ProfessionalCreate,
    professional_status: ProfessionalStatus,
    city_id: UUID,
    db: Session,
) -> Professional:
    """
    Handles a unique username check and password hashing from user data.

    Args:
        professional_create (ProfessionalCreate): DTO for Professional creation.
        professional_status (ProfessionalStatus): The status of the Professional.
        city_id (UUID): The identifier of the city.
        db (Session): Database dependency.

    Raises:
        ApplicationError: If the username already exists in either Company of Professional tables.

    Returns:
        Professional: The newly created Professional model.
    """
    username = professional_create.username
    password = professional_create.password
    email = professional_create.email

    if not unique_username(username=username, db=db):
        raise ApplicationError(
            detail="Username already taken", status_code=status.HTTP_409_CONFLICT
        )
    if not unique_email(email=email, db=db):
        raise ApplicationError(
            detail="Email already taken", status_code=status.HTTP_409_CONFLICT
        )

    hashed_password = hash_password(password=password)

    professional = _create(
        professional_create=professional_create,
        city_id=city_id,
        professional_status=professional_status,
        hashed_password=hashed_password,
        db=db,
    )

    return professional


def _create(
    professional_create: ProfessionalCreate,
    city_id: UUID,
    professional_status: ProfessionalStatus,
    hashed_password: str,
    db: Session,
) -> Professional:
    """
    Handle creation of a Professional entity.

    Args:
        professional_create (ProfessionalCreate): Pydantic DTO for collecting data.
        city_id (UUID): The identifier of the city.
        professional_status (ProfessionalStatus): The status of the Professional upon creation.
        hashed_password (str): Hashed password of the user for insertion into the database.
        db (Session): Database dependency.

    Returns:
        Professional: Newly created entity.
    """

    def _handle_create():
        professional = Professional(
            **professional_create.model_dump(exclude={"city", "password"}),
            city_id=city_id,
            password=hashed_password,
            status=professional_status,
        )
        db.add(professional)
        db.commit()
        db.refresh(professional)
        return professional

    return process_db_transaction(transaction_func=_handle_create, db=db)


def get_skills(professional_id: UUID, db: Session) -> list[SkillResponse]:
    """
    Fetch skillset for professional.

    Args:
        professional_id (UUID): The identifier of the professional.
        db (Session): The database dependency.
    """
    professional = _get_by_id(professional_id=professional_id, db=db)
    professional_job_applications = professional.job_applications
    skills = {
        skill.skill
        for application in professional_job_applications
        for skill in application.skills
    }

    return [
        SkillResponse(id=skill.id, name=skill.name, category_id=skill.category_id)
        for skill in skills
    ]


def get_match_requests(professional_id: UUID, db: Session) -> list[MatchRequestAd]:
    """
    Fetches Match Requests for the given Professional.

    Args:
        professional_id (UUID): The identifier of the Professional.
        db (Session): Database dependency.

    Returns:
        list[MatchRequest]: List of Pydantic models containing basic information about the match request.
    """
    professional = _get_by_id(professional_id=professional_id, db=db)

    match_requests = match_service.get_match_requests_for_professional(
        professional_id=professional.id, db=db
    )

    return match_requests
