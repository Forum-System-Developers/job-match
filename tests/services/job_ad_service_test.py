from datetime import datetime
from unittest.mock import ANY

import pytest

from app.schemas.common import FilterParams, JobAdSearchParams, MessageResponse
from app.schemas.job_ad import JobAdCreate, JobAdUpdate
from app.services.job_ad_service import (
    _update_job_ad,
    add_requirement,
    create,
    get_all,
    get_by_id,
    update,
)
from tests import test_data as td


@pytest.fixture
def mock_db(mocker):
    return mocker.Mock()


def test_getAll_returnsJobAds_whenJobAdsExist(mocker, mock_db) -> None:
    # Arrange
    filter_params = FilterParams(offset=0, limit=10)
    search_params = JobAdSearchParams()
    job_ads = [mocker.Mock(**td.JOB_AD), mocker.Mock(**td.JOB_AD_2)]
    job_ad_responses = [mocker.Mock(), mocker.Mock()]

    mock_query = mock_db.query.return_value
    mock_offset = mock_query.offset.return_value
    mock_limit = mock_offset.limit.return_value
    mock_limit.all.return_value = job_ads

    mock_search_job_ads = mocker.patch(
        "app.services.job_ad_service._search_job_ads", return_value=mock_query
    )
    mock_create = mocker.patch(
        "app.schemas.job_ad.JobAdResponse.create",
        side_effect=job_ad_responses,
    )

    # Act
    result = get_all(filter_params, search_params, mock_db)

    # Assert
    mock_search_job_ads.assert_called_with(search_params=search_params, db=mock_db)
    mock_query.offset.assert_called_with(filter_params.offset)
    mock_offset.limit.assert_called_with(filter_params.limit)
    mock_create.assert_any_call(job_ads[0])
    mock_create.assert_any_call(job_ads[1])
    assert len(result) == 2
    assert result[0] == job_ad_responses[0]
    assert result[1] == job_ad_responses[1]


def test_getAll_returnsEmptyList_whenNoJobAdsExist(mocker, mock_db) -> None:
    # Arrange
    filter_params = FilterParams(offset=0, limit=10)
    search_params = JobAdSearchParams()

    mock_query = mock_db.query.return_value
    mock_offset = mock_query.offset.return_value
    mock_limit = mock_offset.limit.return_value
    mock_limit.all.return_value = []

    mock_search_job_ads = mocker.patch(
        "app.services.job_ad_service._search_job_ads", return_value=mock_query
    )

    # Act
    result = get_all(filter_params, search_params, mock_db)

    # Assert
    mock_search_job_ads.assert_called_with(search_params=search_params, db=mock_db)
    mock_query.offset.assert_called_with(filter_params.offset)
    mock_offset.limit.assert_called_with(filter_params.limit)
    assert result == []


def test_getById_returnsJobAd_whenJobAdExists(mocker, mock_db) -> None:
    # Arrange
    job_ad = mocker.Mock(**td.JOB_AD)
    job_ad_response = mocker.Mock()

    mock_ensure_valid_job_ad_id = mocker.patch(
        "app.services.job_ad_service.ensure_valid_job_ad_id",
        return_value=job_ad,
    )
    mock_create = mocker.patch(
        "app.schemas.job_ad.JobAdResponse.create",
        return_value=job_ad_response,
    )

    # Act
    result = get_by_id(td.VALID_JOB_AD_ID, mock_db)

    # Assert
    mock_ensure_valid_job_ad_id.assert_called_with(
        job_ad_id=td.VALID_JOB_AD_ID,
        db=mock_db,
    )
    mock_create.assert_called_with(job_ad)
    assert result == job_ad_response


def test_create_createsJobAd_whenValidJobAd(mocker, mock_db) -> None:
    # Arrange
    job_ad_data = JobAdCreate(**td.JOB_AD_CREATE)
    mock_company = mocker.Mock(
        id=td.VALID_COMPANY_ID,
        job_ads=list(),
        active_job_count=0,
    )
    mock_job_ad_response = mocker.Mock()

    mock_ensure_valid_company_id = mocker.patch(
        "app.services.job_ad_service.ensure_valid_company_id",
        return_value=mock_company,
    )
    mock_create_response = mocker.patch(
        "app.schemas.job_ad.JobAdResponse.create",
        return_value=mock_job_ad_response,
    )

    # Act
    result = create(company_id=mock_company.id, job_ad_data=job_ad_data, db=mock_db)

    # Assert
    mock_db.add.assert_called_with(ANY)
    mock_db.commit.assert_called()
    mock_db.refresh.assert_called_with(ANY)
    mock_ensure_valid_company_id.assert_called_with(
        id=mock_company.id,
        db=mock_db,
    )
    assert mock_company.active_job_count == 1
    assert len(mock_company.job_ads) == 1
    assert result == mock_job_ad_response


def test_update_updatesJobAd_whenValidData(mocker, mock_db) -> None:
    # Arrange
    job_ad_data = JobAdUpdate(**td.JOB_AD_UPDATE)
    job_ad = mocker.Mock(**td.JOB_AD)
    updated_job_ad = mocker.Mock()
    mock_job_ad_response = mocker.Mock()

    mock_ensure_valid_job_ad_id = mocker.patch(
        "app.services.job_ad_service.ensure_valid_job_ad_id",
        return_value=job_ad,
    )
    mock_update_job_ad = mocker.patch(
        "app.services.job_ad_service._update_job_ad",
        return_value=updated_job_ad,
    )
    mock_create_response = mocker.patch(
        "app.schemas.job_ad.JobAdResponse.create",
        return_value=mock_job_ad_response,
    )

    # Act
    result = update(
        job_ad_id=td.VALID_JOB_AD_ID,
        company_id=td.VALID_COMPANY_ID,
        job_ad_data=job_ad_data,
        db=mock_db,
    )

    # Assert
    mock_ensure_valid_job_ad_id.assert_called_with(
        job_ad_id=td.VALID_JOB_AD_ID,
        db=mock_db,
        company_id=td.VALID_COMPANY_ID,
    )
    mock_update_job_ad.assert_called_with(
        job_ad_data=job_ad_data,
        job_ad=job_ad,
        db=mock_db,
    )
    mock_db.commit.assert_called()
    mock_db.refresh.assert_called_with(updated_job_ad)
    mock_create_response.assert_called_with(updated_job_ad)
    assert result == mock_job_ad_response


def test_addRequirement_addsRequirement_whenValidData(mocker, mock_db) -> None:
    # Arrange
    job_ad = mocker.Mock(**td.JOB_AD, job_ads_requirements=[])
    job_requirement = mocker.Mock()
    message_response = MessageResponse(message="Requirement added to job ad")

    mock_ensure_valid_job_ad_id = mocker.patch(
        "app.services.job_ad_service.ensure_valid_job_ad_id",
        return_value=job_ad,
    )
    mock_ensure_valid_requirement_id = mocker.patch(
        "app.services.job_ad_service.ensure_valid_requirement_id",
        return_value=job_requirement,
    )

    # Act
    result = add_requirement(
        job_ad_id=td.VALID_JOB_AD_ID,
        requirement_id=td.VALID_REQUIREMENT_ID,
        company_id=td.VALID_COMPANY_ID,
        db=mock_db,
    )

    # Assert
    mock_ensure_valid_job_ad_id.assert_called_with(
        job_ad_id=td.VALID_JOB_AD_ID,
        db=mock_db,
        company_id=td.VALID_COMPANY_ID,
    )
    mock_ensure_valid_requirement_id.assert_called_with(
        requirement_id=td.VALID_REQUIREMENT_ID,
        company_id=td.VALID_COMPANY_ID,
        db=mock_db,
    )
    mock_db.add.assert_called_with(ANY)
    mock_db.commit.assert_called()
    mock_db.refresh.assert_called_with(ANY)
    assert result == message_response


def test_updateJobAd_updatesTitle_whenTitleIsProvided(mocker, mock_db) -> None:
    # Arrange
    mock_job_ad = mocker.Mock(**td.JOB_AD)
    job_ad_update_data = JobAdUpdate(title=td.VALID_JOB_AD_TITLE_2)

    mock_ensure_valid_city = mocker.patch(
        "app.services.job_ad_service.ensure_valid_city"
    )

    # Act
    result = _update_job_ad(
        job_ad_data=job_ad_update_data,
        job_ad=mock_job_ad,
        db=mock_db,
    )

    # Assert
    mock_ensure_valid_city.assert_not_called()
    assert result.title == job_ad_update_data.title
    assert isinstance(result.updated_at, datetime)

    assert result.description == mock_job_ad.description
    assert result.location == mock_job_ad.location
    assert result.min_salary == mock_job_ad.min_salary
    assert result.max_salary == mock_job_ad.max_salary
    assert result.status == mock_job_ad.status


def test_updateJobAd_updatesDescription_whenDescriptionIsProvided(mocker, mock_db) -> None:
    # Arrange
    mock_job_ad = mocker.Mock(**td.JOB_AD)
    job_ad_update_data = JobAdUpdate(description=td.VALID_JOB_AD_DESCRIPTION_2)

    mock_ensure_valid_city = mocker.patch(
        "app.services.job_ad_service.ensure_valid_city"
    )

    # Act
    result = _update_job_ad(
        job_ad_data=job_ad_update_data,
        job_ad=mock_job_ad,
        db=mock_db,
    )

    # Assert
    mock_ensure_valid_city.assert_not_called()
    assert result.description == job_ad_update_data.description
    assert isinstance(result.updated_at, datetime)

    assert result.title == mock_job_ad.title
    assert result.location == mock_job_ad.location
    assert result.min_salary == mock_job_ad.min_salary
    assert result.max_salary == mock_job_ad.max_salary
    assert result.status == mock_job_ad.status


def test_updateJobAd_updatesLocation_whenLocationIsProvided(mocker, mock_db) -> None:
    # Arrange
    mock_job_ad = mocker.Mock(**td.JOB_AD)
    mock_location = mocker.Mock(id=td.VALID_CITY_ID_2)
    job_ad_update_data = JobAdUpdate(location=td.VALID_CITY_NAME_2)

    mock_ensure_valid_city = mocker.patch(
        "app.services.job_ad_service.ensure_valid_city",
        return_value=mock_location,
    )

    # Act
    result = _update_job_ad(
        job_ad_data=job_ad_update_data,
        job_ad=mock_job_ad,
        db=mock_db,
    )

    # Assert
    mock_ensure_valid_city.assert_called_with(
        name=job_ad_update_data.location,
        db=mock_db,
    )
    assert result.location == mock_location
    assert isinstance(result.updated_at, datetime)

    assert result.title == mock_job_ad.title
    assert result.description == mock_job_ad.description
    assert result.min_salary == mock_job_ad.min_salary
    assert result.max_salary == mock_job_ad.max_salary
    assert result.status == mock_job_ad.status
