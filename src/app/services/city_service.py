import logging
from uuid import UUID

from app.schemas.city import CityResponse
from app.services.external_db_service_urls import (
    CITIES_URL,
    CITY_BY_ID_URL,
    CITY_BY_NAME_URL,
)
from app.utils.request_handlers import perform_get_request

logger = logging.getLogger(__name__)


def get_by_name(city_name: str) -> CityResponse:
    """
    Retrieves an instance of the City model by its name.

    Args:
        city_name (str): The Name of the City.

    Returns:
        CityResponse: Pydantic response model for City.

    Raises:
        Application Error (status_code_404) If the City is not found.
    """
    city = perform_get_request(url=CITY_BY_NAME_URL.format(city_name=city_name))
    logger.info(f"City {city} fetched")

    return CityResponse(**city)


def get_by_id(city_id: UUID) -> CityResponse:
    """
    Retrieves an instance of the City model.

    Args:
        city_id (UUID): The identifier of the city.

    Returns:
        CityResponse: Pydantic reponse model for City.
    """
    city = perform_get_request(url=CITY_BY_ID_URL.format(city_id=city_id))
    logger.info(f"City {city} fetched")

    return CityResponse(**city)


def get_all() -> list[CityResponse]:
    """
    Retrieves all cities from the database.

    Returns:
        list[CityResponse]: A list of CityResponse objects representing all cities in the database.
    """
    cities = perform_get_request(url=CITIES_URL)

    return [CityResponse(**city) for city in cities]
