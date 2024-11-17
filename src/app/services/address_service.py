import logging
from uuid import UUID

from fastapi import status
from sqlalchemy.orm import Session

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.address import CityResponse
from app.sql_app.city.city import City

logger = logging.getLogger(__name__)


def get_by_name(name: str, db: Session) -> CityResponse:
    """
    Retrieves an instance of the City model.

    Args:
        name (str): The Name of the City.
        db (Session): The database dependency.

    Returns:
        CityResponse: Pydantic response model for City.
    """
    city = db.query(City).filter(City.name == name).first()
    if city is None:
        logger.error(f"City name {name} not found")
        raise ApplicationError(
            detail=f"City with name {name} was not found",
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
    city = db.query(City).filter(City.id == city_id).first()
    if city is None:
        logger.error(f"City with id {city_id} not found")
        raise ApplicationError(
            detail=f"City with id {city_id} was not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    logger.info(f"City {city} fetched")

    return CityResponse(id=city.id, name=city.name)
