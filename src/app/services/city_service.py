import logging
from uuid import UUID

from fastapi import status
from sqlalchemy.orm import Session

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.city import CityResponse
from app.sql_app.city.city import City

logger = logging.getLogger(__name__)


def get_by_name(city_name: str, db: Session) -> CityResponse:
    """
    Retrieves an instance of the City model by its name.

    Args:
        city_name (str): The Name of the City.
        db (Session): The database dependency.

    Returns:
        CityResponse: Pydantic response model for City.

    Raises:
        Application Error (status_code_404) If the City is not found.
    """
    city: City | None = db.query(City).filter(City.name == city_name).first()
    if city is None:
        logger.error(f"City name {city_name} not found")
        raise ApplicationError(
            detail=f"City with name {city_name} was not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    logger.info(f"City {city} fetched")

    return CityResponse(id=city.id, name=city.name)


def get_by_id(city_id: UUID, db: Session) -> CityResponse:
    """
    Retrieves an instance of the City model.

    Args:
        city_id (UUID): The identifier of the city.
        db (Session): The database dependency.

    Returns:
        CityResponse: Pydantic reponse model for City.
    """
    city: City | None = db.query(City).filter(City.id == city_id).first()
    if city is None:
        logger.error(f"City with id {city_id} not found")
        raise ApplicationError(
            detail=f"City with id {city_id} was not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    logger.info(f"City {city} fetched")

    return CityResponse(id=city.id, name=city.name)


def get_id(db: Session, city_name: str) -> UUID:
    """
    Fetches the identifier of a City by its name.

    Args:
        db (Session): Database dependency.
        city_name (str): The name of the City.

    Returns:
        UUID
    """
    city: City | None = db.query(City).filter(City.name == city_name).first()
    if city is None:
        raise ApplicationError(
            detail=f"City with name {city_name} not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return city.id
