import pytest

from app.schemas.common import MessageResponse
from app.services.match_service import accept_job_application_match_request
from app.sql_app.job_ad.job_ad_status import JobAdStatus
from app.sql_app.job_application.job_application_status import JobStatus
from app.sql_app.match.match_status import MatchStatus
from tests import test_data as td


@pytest.fixture
def mock_db(mocker):
    return mocker.Mock()


def test_acceptJobApplicationMatchRequest_acceptsMatchRequest_whenValidData(
    mocker, mock_db
) -> None:
    # Arrange
    job_ad = mocker.Mock(**td.JOB_AD)
    job_ad.company.successfull_matches_count = 0
    job_application = mocker.Mock(**td.JOB_APPLICATION)
    match = mocker.Mock(**td.MATCH)

    mock_ensure_valid_job_ad_id = mocker.patch(
        "app.services.match_service.ensure_valid_job_ad_id",
        return_value=job_ad,
    )
    mock_ensure_valid_job_application_id = mocker.patch(
        "app.services.match_service.ensure_valid_job_application_id",
        return_value=job_application,
    )
    mock_ensure_valid_match_request = mocker.patch(
        "app.services.match_service.ensure_valid_match_request",
        return_value=match,
    )

    # Act
    result = accept_job_application_match_request(
        job_ad_id=td.VALID_JOB_AD_ID,
        job_application_id=td.VALID_JOB_APPLICATION_ID,
        company_id=td.VALID_COMPANY_ID,
        db=mock_db,
    )

    # Assert
    mock_ensure_valid_job_ad_id.assert_called_with(
        job_ad_id=job_ad.id,
        db=mock_db,
        company_id=job_ad.company_id,
    )
    mock_ensure_valid_job_application_id.assert_called_with(
        id=job_application.id,
        db=mock_db,
    )
    mock_ensure_valid_match_request.assert_called_with(
        job_ad_id=job_ad.id,
        job_application_id=job_application.id,
        match_status=MatchStatus.REQUESTED_BY_JOB_APP,
        db=mock_db,
    )
    assert job_ad.status == JobAdStatus.ARCHIVED
    assert job_application.status == JobStatus.MATCHED
    assert match.status == MatchStatus.ACCEPTED
    assert job_ad.company.successfull_matches_count == 1
    mock_db.commit.assert_called()
    assert isinstance(result, MessageResponse)
