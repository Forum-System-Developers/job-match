import pytest

from app.schemas.common import FilterParams, JobAdSearchParams
from app.services.job_ad_service import get_all, get_by_id
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
