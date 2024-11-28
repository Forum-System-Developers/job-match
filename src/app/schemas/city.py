from uuid import UUID

from pydantic import BaseModel


class City(BaseModel):
    """
    City schema representing a city with an ID and a name.

    Attributes:
        id (UUID): Unique identifier for the city.
        name (str): Name of the city.
    """

    id: UUID
    name: str


class CityResponse(City):
    """
    CityResponse schema representing the response structure for city-related data.

    Attributes:
        id (UUID): Unique identifier for the city.
        name (str): Name of the city.
    """

    pass
