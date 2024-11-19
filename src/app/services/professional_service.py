import logging
from uuid import UUID

from fastapi import UploadFile, status
from sqlalchemy.orm import Session, joinedload

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.common import FilterParams, SearchParams
from app.schemas.job_ad import BaseJobAd
from app.schemas.job_application import JobApplicationResponse, JobSearchStatus
from app.schemas.professional import (
    PrivateMatches,
    ProfessionalCreate,
    ProfessionalRequestBody,
    ProfessionalResponse,
    ProfessionalUpdate,
)
from app.schemas.user import User
from app.services import city_service
from app.sql_app.job_ad.job_ad import JobAd
from app.sql_app.job_application.job_application import JobApplication
from app.sql_app.job_application.job_application_status import JobStatus
from app.sql_app.job_application_skill.job_application_skill import JobApplicationSkill
from app.sql_app.match.match import Match
from app.sql_app.professional.professional import Professional
from app.sql_app.professional.professional_status import ProfessionalStatus
from app.sql_app.skill.skill import Skill

logger = logging.getLogger(__name__)


def create(
    professional_request: ProfessionalRequestBody,
    db: Session,
    # photo: UploadFile | None = None,
) -> ProfessionalResponse:
    """
    Creates an instance of the Professional model.

    Args:
        professional_request (ProfessionalRequestBody): Pydantic schema for collecting data.
        db (Session): Database dependency.
        photo (UploadFile | None): Photo of the professional.

    Returns:
        Professional: Pydantic response model for Professional.
    """
    professional_create = professional_request.professional
    professional_status = professional_request.status

    city = city_service.get_by_name(city_name=professional_create.city, db=db)
    if city is None:
        logger.error(f"City name {professional_create.city} not found")
        raise ApplicationError(
            detail=f"City with name {professional_create.city} was not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    logger.info(f"City {city} fetched")

    # if photo is not None:
    #     upload_photo = photo.file.read()

    professional = Professional(
        **professional_create.model_dump(exclude={"city"}),
        # photo=upload_photo,
        city_id=city.id,
        status=professional_status,
    )

    db.add(professional)
    db.commit()
    db.refresh(professional)

    logger.info(f"Professional with id {professional.id} created")
    return ProfessionalResponse.create(professional=professional)


def update(
    professional_id: UUID,
    professional_update: ProfessionalUpdate,
    professional_status: ProfessionalStatus,
    private_matches: PrivateMatches,
    db: Session,
    photo: UploadFile | None = None,
) -> ProfessionalResponse:
    """
    Upates an instance of the Professional model.

    Args:
        professional_id (UUID): The identifier of the professional.
        professional_update (ProfessionalUpdate): Pydantic schema for collecting data.
        professional_status (ProfessionalStatus): The status of the Professional.
        db (Session): Database dependency.
        photo (UploadFile | None): Photo of the professional.

    Returns:
        Professional: Professional Pydantic response model.

    Raises:
        ApplicationError: If the professional with the given id is
            not found in the database.
        ApplicationError: If the city with the given name is
            not found in the database.

    """
    professional = _get_by_id(professional_id=professional_id, db=db)

    professional = _update_atributes(
        professional_update=professional_update,
        professional=professional,
        db=db,
        professional_status=professional_status,
        private_matches=private_matches,
    )

    if photo is not None:
        upload_photos = photo.file.read()
        professional.photo = upload_photos
        logger.info("Professional photo updated successfully")

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

    if search_params.skills:
        query = query.filter(Skill.name.in_(search_params.skills))
        logger.info(f"Filtered Professionals by skills: {search_params.skills}")

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


def _get_matches(professional_id: UUID, db: Session) -> list[BaseJobAd]:
    """
    Fetches Matched Job Ads for the given Professional.

    Args:
        professional (Professional): The existing professional object to be updated.        db (Session): Database dependency.

    Returns:
        list[BaseJobAd]: List of Pydantic models containing basic information about the matched Job Ad.
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

    return [BaseJobAd.model_validate(ad) for ad in ads]


def _update_atributes(
    professional_update: ProfessionalUpdate,
    professional: Professional,
    private_matches: PrivateMatches,
    db: Session,
    professional_status: ProfessionalStatus,
) -> Professional:
    """
    Updates the attributes of a professional's profile based on the provided ProfessionalUpdate model.

    Args:
        professional_update (ProfessionalUpdate): The updated information for the professional.
        professional (Professional): The existing professional object to be updated.
        private_matches (PrivateMatches): Indicates if the professional has private matches.
        db (Session): The database session used for querying or interacting with the database.
        professional_status (ProfessionalStatus): The new professional status to be applied if different.

    Returns:
        Professional (Professional): The updated professional object with modified attributes.
    """
    if professional.status != professional_status:
        professional.status = professional_status
        logger.info("Professional status updated successfully")

    if (
        professional_update.city is not None
        and professional_update.city != professional.city.name
    ):
        city = city_service.get_by_name(city_name=professional_update.city, db=db)
        professional.city_id = city.id
        logger.info("professional city updated successfully")

    if (
        professional_update.description is not None
        and professional.description != professional_update.description
    ):
        professional.description = professional_update.description
        logger.info("Professional description updated successfully")

    if (
        professional_update.first_name
        and professional.first_name != professional_update.first_name
    ):
        professional.first_name = professional_update.first_name
        logger.info("Professional first name updated successfully")

    if (
        professional_update.last_name
        and professional.last_name != professional_update.last_name
    ):
        professional.last_name = professional_update.last_name
        logger.info("Professional last name updated successfully")

    professional.has_private_matches = private_matches.value

    return professional


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

    applications = (
        db.query(JobApplication)
        .filter(
            JobApplication.professional_id == professional_id,
            JobApplication.status == application_status.value,
        )
        .offset(filter_params.offset)
        .limit(filter_params.limit)
        .all()
    )

    return [
        JobApplicationResponse.create(
            professional=professional, job_application=application
        )
        for application in applications
    ]
