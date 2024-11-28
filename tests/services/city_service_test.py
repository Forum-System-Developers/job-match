from unittest.mock import ANY

import pytest
from fastapi import status

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.city import CityResponse
from app.services.city_service import get_by_id, get_by_name, get_id
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


def test_getByName_raises_error_when_city_is_not_found(mock_db):
    # Arrange
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = None

    # Act
    with pytest.raises(ApplicationError) as exc:
        get_by_name(city_name=td.VALID_CITY_NAME, db=mock_db)

    # Assert
    mock_db.query.assert_called_once_with(City)
    assert_filter_called_with(mock_query, City.name == td.VALID_CITY_NAME)
    assert exc.value.data.status == status.HTTP_404_NOT_FOUND
    assert exc.value.data.detail == f"City with name {td.VALID_CITY_NAME} was not found"


def test_getById_returns_city_when_city_is_found(mocker, mock_db):
    # Arrange
    city = mocker.Mock()
    city.id = td.VALID_CITY_ID
    city.name = td.VALID_CITY_NAME

    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = city

    expected_city_response = CityResponse(id=td.VALID_CITY_ID, name=td.VALID_CITY_NAME)

    # Act
    result = get_by_id(city_id=td.VALID_CITY_ID, db=mock_db)

    # Assert
    mock_db.query.assert_called_once_with(City)
    mock_query.filter.assert_called_once_with(ANY)
    assert_filter_called_with(mock_query, City.id == td.VALID_CITY_ID)
    assert result == expected_city_response


def test_getById_raises_error_when_city_is_not_found(mock_db):
    # Arrange
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = None

    # Act
    with pytest.raises(ApplicationError) as exc:
        get_by_id(city_id=td.VALID_CITY_ID, db=mock_db)

    # Assert
    mock_db.query.assert_called_once_with(City)
    assert_filter_called_with(mock_query, City.id == td.VALID_CITY_ID)
    assert exc.value.data.status == status.HTTP_404_NOT_FOUND
    assert exc.value.data.detail == f"City with id {td.VALID_CITY_ID} was not found"


def test_getId_returns_city_id_when_city_is_found(mocker, mock_db):
    # Arrange
    city = mocker.Mock()
    city.id = td.VALID_CITY_ID
    city.name = td.VALID_CITY_NAME

    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = city

    # Act
    result = get_id(db=mock_db, city_name=td.VALID_CITY_NAME)

    # Assert
    mock_db.query.assert_called_once_with(City)
    mock_query.filter.assert_called_once_with(ANY)
    assert_filter_called_with(mock_query, City.name == td.VALID_CITY_NAME)
    assert result == td.VALID_CITY_ID


def test_getId_raises_error_when_city_is_not_found(mock_db):
    # Arrange
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = None

    # Act
    with pytest.raises(ApplicationError) as exc:
        get_id(db=mock_db, city_name=td.VALID_CITY_NAME)

    # Assert
    mock_db.query.assert_called_once_with(City)
    assert_filter_called_with(mock_query, City.name == td.VALID_CITY_NAME)
    assert exc.value.data.status == status.HTTP_404_NOT_FOUND
    assert exc.value.data.detail == f"City with name {td.VALID_CITY_NAME} not found."
