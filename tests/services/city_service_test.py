from unittest.mock import ANY

import pytest

from app.schemas.address import CityResponse
from app.services.city_service import get_by_name
from app.sql_app.city.city import City
from tests import test_data as td
from tests.utils import assert_filter_called_with


@pytest.fixture
def mock_db(mocker):
    return mocker.Mock()


def test_getByName_returns_city_when_city_is_found(mocker, mock_db):
    # Arrange
    city = mocker.Mock()
    city.id = td.VALID_CITY_ID
    city.name = td.VALID_CITY_NAME

    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = city

    expected_city_response = CityResponse(id=td.VALID_CITY_ID, name=td.VALID_CITY_NAME)

    # Act
    result = get_by_name(city_name=td.VALID_CITY_NAME, db=mock_db)

    # Assert
    mock_db.query.assert_called_once_with(City)
    mock_query.filter.assert_called_once_with(ANY)
    assert_filter_called_with(mock_query, City.name == td.VALID_CITY_NAME)
    assert result == expected_city_response
