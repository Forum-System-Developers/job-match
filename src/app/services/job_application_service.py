import logging
from uuid import UUID

from fastapi import status
from sqlalchemy.orm import Session

from app.exceptions.custom_exceptions import ApplicationError
from app.sql_app.job_application.job_application import JobApplication
from app.schemas.job_application import JobAplicationBase, JobApplicationResponse
from app.sql_app.user.user import User

logger = logging.getLogger(__name__)


def create(
    user: User,
    application: JobAplicationBase,
    db: Session,
) -> JobApplicationResponse:
    """
    Creates an instance of the Job Application model.

    Args:
        user (User): Current logged in user.
        application (ProfessionalBase): Pydantic schema for collecting data.
        db (Session): Database dependency.

    Returns:
        JobApplicationResponse: Professional Pydantic response model.
    """

    # return ProfessionalResponse.model_validate(professional, from_attributes=True)


# def update(
#     professional_id: UUID,
#     professional_update: ProfessionalBase,
#     professional_status: ProfessionalStatus,
#     db: Session,
#     photo: UploadFile | None = None,
# ) -> ProfessionalResponse:
#     """
#     Upates an instance of the Professional model.

#     Args:
#         professional_id (UUID): The identifier of the professional.
#         professional_update (ProfessionalBase): Pydantic schema for collecting data.
#         professional_status (ProfessionalStatus): The status of the Professional.
#         db (Session): Database dependency.
#         photo (UploadFile | None): Photo of the professional.

#     Returns:
#         Professional: Professional Pydantic response model.
#     """
#     professional = _get_by_id(professional_id=professional_id, db=db)
#     if professional is None:
#         logger.error(f"Professional with id {professional_id} not found")
#         raise ApplicationError(
#             detail=f"Professional with ID {professional_id} was not found",
#             status_code=status.HTTP_404_NOT_FOUND,
#         )

#     logger.info(f"Professional with ID {professional_id} fetched")

#     city = address_service.get_by_name(name=professional_update.city, db=db)
#     if city is None:
#         logger.error(f"City name {professional_update.city} not found")
#         raise ApplicationError(
#             detail=f"City with name {professional_update.city} was not found",
#             status_code=status.HTTP_404_NOT_FOUND,
#         )
#     logger.info(f"City {city} fetched")

#     if not professional:
#         logger.error(f"Professional with id {professional_id} not found")
#         raise ApplicationError(
#             detail="Professional not found", status_code=status.HTTP_404_NOT_FOUND
#         )

#     if professional.city_id != city.id:
#         professional.city_id = city.id
#         logger.info("professional city updated successfully")

#     if professional.description != professional_update.description:
#         professional.description = professional_update.description
#         logger.info("Professional description updated successfully")

#     if professional.status != professional_status:
#         professional.status = professional_status
#         logger.info("Professional status updated successfully")

#     if professional.first_name != professional_update.first_name:
#         professional.first_name = professional_update.first_name
#         logger.info("Professional first name updated successfully")

#     if professional.last_name != professional_update.last_name:
#         professional.last_name = professional_update.last_name
#         logger.info("Professional last name updated successfully")

#     if photo is not None:
#         updload_photo = photo.file.read()
#         professional.photo = updload_photo
#         logger.info("Professional photo updated successfully")

#     db.commit()
#     db.refresh(professional)

#     logger.info(f"Professional with id {professional.id} updated successfully")
#     return ProfessionalResponse.model_validate(professional, from_attributes=True)


# def get_all(db: Session, filter_params: FilterParams) -> list[ProfessionalResponse]:
#     """
#     Retrieve all Professional profiles.

#     Args:
#         db (Session): The database session.
#         filer_params (FilterParams): Pydantic schema for filtering params.
#     Returns:
#         list[ProfessionalResponse]: A list of Professional Profiles that are visible for Companies.
#     """

#     query = db.query(Professional).filter(
#         Professional.status == ProfessionalStatus.ACTIVE
#     )
#     logger.info("Retreived all professional profiles that are with status ACTIVE")

#     query = query.offset(filter_params.offset).limit(filter_params.limit).all()
#     logger.info("Limited public topics based on offset and limit")

#     return [
#         ProfessionalResponse.model_validate(professional, from_attributes=True)
#         for professional in query
#     ]


# def _get_by_id(professional_id: UUID, db: Session) -> Professional | None:
#     """
#     Retrieves an instance of the Professional model or None.

#     Args:
#         professional_id (UUID): The identifier.
#         db (Session): Database dependency.

#     Returns:
#         Professional: SQLAlchemy model for Professional.
#     """
#     professional = (
#         db.query(Professional).filter(Professional.id == professional_id).first()
#     )

#     return professional


# def get_by_id(professional_id: UUID, db: Session) -> ProfessionalResponse:
#     professional = _get_by_id(professional_id=professional_id, db=db)
#     if professional is None:
#         logger.error(f"Professional with id {professional_id} not found")
#         raise ApplicationError(
#             detail=f"Professional with id {professional_id} not found",
#             status_code=status.HTTP_404_NOT_FOUND,
#         )

#     logger.info(f"Professional with id {professional.id} created")
#     return ProfessionalResponse.model_validate(professional, from_attributes=True)
