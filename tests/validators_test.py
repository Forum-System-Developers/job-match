import uuid

import pytest
from fastapi import status

from app.exceptions.custom_exceptions import ApplicationError
from app.services.utils.validators import (
    ensure_no_match_request,
    ensure_valid_company_id,
    ensure_valid_job_ad_id,
    ensure_valid_job_application_id,
    ensure_valid_location,
    ensure_valid_match_request,
    ensure_valid_professional_id,
    ensure_valid_requirement_id,
    unique_email,
    unique_username,
)
from app.sql_app import (
    City,
    Company,
    JobAd,
    JobApplication,
    JobRequirement,
    Match,
    Professional,
)
from tests.utils import assert_filter_called_with
from tests import test_data as td


@pytest.fixture
def mock_db(mocker):
    return mocker.Mock()


def test_ensureValidLocation_returnsCity_whenLocationIsFound(mocker, mock_db):
    # Arrange
    city = mocker.Mock(name=td.VALID_CITY_NAME)

    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = city

    # Act
    result = ensure_valid_location(location=td.VALID_CITY_NAME, db=mock_db)

    # Assert
    mock_db.query.assert_called_once_with(City)
    assert_filter_called_with(mock_query, City.name == td.VALID_CITY_NAME)
    assert result == city
