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


def test_ensureValidLocation_raisesApplicationError_whenLocationIsNotFound(mock_db):
    # Arrange
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = None

    # Act
    with pytest.raises(ApplicationError) as exc:
        ensure_valid_location(location=td.VALID_CITY_NAME, db=mock_db)

    # Assert
    mock_db.query.assert_called_once_with(City)
    assert_filter_called_with(mock_query, City.name == td.VALID_CITY_NAME)
    assert exc.value.data.status == status.HTTP_404_NOT_FOUND
    assert exc.value.data.detail == f"City with name {td.VALID_CITY_NAME} not found"


def test_ensureValidJobAdId_returnsJobAd_whenJobAdIsFound(mocker, mock_db):
    # Arrange
    job_ad = mocker.Mock(id=td.VALID_JOB_AD_ID)

    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = job_ad

    # Act
    result = ensure_valid_job_ad_id(job_ad_id=td.VALID_JOB_AD_ID, db=mock_db)

    # Assert
    mock_db.query.assert_called_once_with(JobAd)
    assert_filter_called_with(mock_query, JobAd.id == td.VALID_JOB_AD_ID)
    assert result == job_ad


def test_ensureValidJobAdId_returnsJobAd_whenCompanyIsProvided(mocker, mock_db):
    # Arrange
    job_ad = mocker.Mock(id=td.VALID_JOB_AD_ID, company_id=td.VALID_COMPANY_ID)

    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = job_ad

    # Act
    result = ensure_valid_job_ad_id(
        job_ad_id=td.VALID_JOB_AD_ID,
        db=mock_db,
        company_id=td.VALID_COMPANY_ID,
    )

    # Assert
    mock_db.query.assert_called_once_with(JobAd)
    assert_filter_called_with(mock_query, JobAd.id == td.VALID_JOB_AD_ID)
    assert result == job_ad


def test_ensureValidJobAdId_raisesApplicationError_whenJobAdIsNotFound(mock_db):
    # Arrange
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = None

    # Act
    with pytest.raises(ApplicationError) as exc:
        ensure_valid_job_ad_id(job_ad_id=td.NON_EXISTENT_ID, db=mock_db)

    # Assert
    mock_db.query.assert_called_once_with(JobAd)
    assert_filter_called_with(mock_query, JobAd.id == td.NON_EXISTENT_ID)
    assert exc.value.data.status == status.HTTP_404_NOT_FOUND
    assert exc.value.data.detail == f"Job Ad with id {td.NON_EXISTENT_ID} not found"


def test_ensureValidJobAdId_raisesApplicationError_whenJobAdDoesNotBelongToCompany(
    mocker, mock_db
):
    # Arrange
    job_ad = mocker.Mock(id=td.VALID_JOB_AD_ID, company_id=td.NON_EXISTENT_ID)

    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = job_ad

    # Act
    with pytest.raises(ApplicationError) as exc:
        ensure_valid_job_ad_id(
            job_ad_id=td.VALID_JOB_AD_ID, company_id=td.VALID_COMPANY_ID, db=mock_db
        )

    # Assert
    mock_db.query.assert_called_once_with(JobAd)
    assert_filter_called_with(mock_query, JobAd.id == td.VALID_JOB_AD_ID)
    assert exc.value.data.status == status.HTTP_400_BAD_REQUEST
    assert (
        exc.value.data.detail
        == f"Job Ad with id {td.VALID_JOB_AD_ID} does not belong to company with id {td.VALID_COMPANY_ID}"
    )
