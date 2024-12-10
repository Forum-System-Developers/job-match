import pytest

from app.schemas.city import CityResponse
from app.services import city_service
from app.services.external_db_service_urls import CITIES_URL, CITY_BY_ID_URL, CITY_BY_NAME_URL
from tests import test_data as td


def test_getByName_returnsCity_whenCityExists(mocker) -> None:
    # Arrange
    city = td.CITY
    mock_perform_get_request = mocker.patch(
        "app.services.city_service.perform_get_request",
        return_value=city,
    )
    mock_city_response = mocker.patch(
        "app.services.city_service.CityResponse",
        return_value=mocker.Mock(spec=CityResponse),
    )

    # Act
    result = city_service.get_by_name(city_name=td.VALID_CITY_NAME)

    # Assert
    mock_perform_get_request.assert_called_once_with(
        url=CITY_BY_NAME_URL.format(city_name=td.VALID_CITY_NAME)
    )
    mock_city_response.assert_called_once_with(**city)
    assert isinstance(result, CityResponse)


def test_getById_returnsCity_whenCityExists(mocker) -> None:
    # Arrange
    city = td.CITY
    mock_perform_get_request = mocker.patch(
        "app.services.city_service.perform_get_request",
        return_value=city,
    )
    mock_city_response = mocker.patch(
        "app.services.city_service.CityResponse",
        return_value=mocker.Mock(spec=CityResponse),
    )

    # Act
    result = city_service.get_by_id(city_id=td.VALID_CITY_ID)

    # Assert
    mock_perform_get_request.assert_called_once_with(
        url=CITY_BY_ID_URL.format(city_id=td.VALID_CITY_ID)
    )
    mock_city_response.assert_called_once_with(**city)
    assert isinstance(result, CityResponse)

def test_getAll_returnsListOfCities_whenCitiesExist(mocker) -> None:
    # Arrange
    cities = [td.CITY, td.CITY_2]
    mock_perform_get_request = mocker.patch(
        "app.services.city_service.perform_get_request",
        return_value=cities,
    )
    mock_city_response = mocker.patch(
        "app.services.city_service.CityResponse",
        side_effect=[mocker.Mock(spec=CityResponse), mocker.Mock(spec=CityResponse)],
    )

    # Act
    result = city_service.get_all()

    # Assert
    mock_perform_get_request.assert_called_once_with(url=CITIES_URL)
    assert mock_city_response.call_count == len(cities)
    assert all(isinstance(city, CityResponse) for city in result)
    assert len(result) == len(cities)
    