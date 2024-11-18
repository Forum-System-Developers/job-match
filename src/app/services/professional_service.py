import logging
from uuid import UUID

from fastapi import UploadFile, status
from sqlalchemy.orm import Session, joinedload

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.common import FilterParams
from app.schemas.job_ad import BaseJobAd
from app.schemas.professional import (
    ProfessionalCreate,
    ProfessionalResponse,
    ProfessionalUpdate,
)
from app.schemas.user import UserResponse
from app.services import city_service
from app.sql_app.job_application.job_application import JobApplication
from app.sql_app.job_application.job_application_status import JobStatus
from app.sql_app.professional.professional import Professional
from app.sql_app.professional.professional_status import ProfessionalStatus

logger = logging.getLogger(__name__)


def create(
    user: UserResponse,
    professional_create: ProfessionalCreate,
    professional_status: ProfessionalStatus,
    db: Session,
    photo: UploadFile | None = None,
) -> ProfessionalResponse:
    """
    Creates an instance of the Professional model.

    Args:
        user (UserResponse): Current logged in user.
        professional_create (ProfessionalCreate): Pydantic schema for collecting data.
        professional_status (ProfessionalStatus): The status of the Professional.
        db (Session): Database dependency.
        photo (UploadFile | None): Photo of the professional.

    Returns:
        Professional: Professional Pydantic response model.
    """
    city = city_service.get_by_name(city_name=professional_create.city, db=db)
    if city is None:
        logger.error(f"City name {professional_create.city} not found")
        raise ApplicationError(
            detail=f"City with name {professional_create.city} was not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    logger.info(f"City {city} fetched")

    if photo is not None:
        upload_photo = photo.file.read()

    professional = Professional(
        **professional_create.model_dump(exclude={"city"}),
        photo=upload_photo,
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
    private_matches: bool,
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
        get_matches(professional_id=professional_id, db=db)
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
        get_matches(professional_id=professional_id, db=db)
        if not professional.has_private_matches
        else None
    )

    return ProfessionalResponse.create(
        professional=professional, matched_ads=matched_ads
    )


def get_all(db: Session, filter_params: FilterParams) -> list[ProfessionalResponse]:
    """
    Retrieve all Professional profiles.

    Args:
        db (Session): The database session.
        filer_params (FilterParams): Pydantic schema for filtering params.
    Returns:
        list[ProfessionalResponse]: A list of Professional Profiles that are visible for Companies.
    """

    query = db.query(Professional).filter(
        Professional.status == ProfessionalStatus.ACTIVE
    )

    logger.info("Retreived all professional profiles that are with status ACTIVE")

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


def get_matches(professional_id: UUID, db: Session) -> list[BaseJobAd]:
    """
    Fetches Matched Job Ads for the given Professional.

    Args:
        professional (Professional): The existing professional object to be updated.
        private_matches (bool): Indicates if the professional has private matches.
        db (Session): Database dependency.

    Returns:
        list[BaseJobAd]: List of Pydantic models containing basic information about the matched Job Ad.
    """
    professional = (
        db.query(Professional)
        .options(
            joinedload(Professional.job_applications).joinedload(JobApplication.matches)
        )
        .filter(Professional.id == professional_id)
        .first()
    )

    ads = [
        match.job_ad
        for job_application in professional.job_applications
        if job_application.status == JobStatus.MATCHED
        for match in job_application.matches
    ]

    return [
        BaseJobAd(
            title=ad.title,
            description=ad.description,
            location=ad.location.name,
            min_salary=ad.min_salary,
            max_salary=ad.max_salary,
        )
        for ad in ads
    ]


def _update_atributes(
    professional_update: ProfessionalUpdate,
    professional: Professional,
    private_matches: bool,
    db: Session,
    professional_status: ProfessionalStatus,
) -> Professional:
    """
    Updates the attributes of a professional's profile based on the provided ProfessionalUpdate model.

    Args:
        professional_update (ProfessionalUpdate): The updated information for the professional.
        professional (Professional): The existing professional object to be updated.
        private_matches (bool): Indicates if the professional has private matches.
        db (Session): The database session used for querying or interacting with the database.
        professional_status (ProfessionalStatus): The new professional status to be applied if different.

    Returns:
        Professional: The updated professional object with modified attributes.
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

    professional.has_private_matches = private_matches

    return professional
