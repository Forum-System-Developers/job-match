from unittest.mock import call

import pytest
from fastapi import status

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.city import City
from app.schemas.common import FilterParams, MessageResponse
from app.schemas.job_application import MatchResponseRequest
from app.schemas.match import MatchRequestAd, MatchResponse
from app.services.match_service import (
    _get_match,
    accept_job_application_match_request,
    accept_match_request,
    get_company_match_requests,
    get_match_requests_for_job_application,
    process_request_from_company,
    reject_match_request,
    send_job_application_match_request,
    view_received_job_application_match_requests,
    view_sent_job_application_match_requests,
)
from app.sql_app.job_ad.job_ad import JobAd
from app.sql_app.job_ad.job_ad_status import JobAdStatus
from app.sql_app.job_application.job_application_status import JobStatus
from app.sql_app.match.match import Match
from app.sql_app.match.match_status import MatchStatus
from app.sql_app.professional.professional_status import ProfessionalStatus
from tests import test_data as td
from tests.utils import assert_called_with, assert_filter_called_with


@pytest.fixture
def mock_db(mocker):
    return mocker.Mock()


@pytest.fixture
def mock_job_ads(mocker):
    return [
        mocker.Mock(**td.JOB_AD, location=City(**td.CITY)),
        mocker.Mock(**td.JOB_AD_2, location=City(**td.CITY_2)),
    ]


def test_getMatch_returnsMatch_whenValidData(mocker, mock_db) -> None:
    # Arrange
    job_application = mocker.Mock(**td.JOB_APPLICATION)
    job_ad = mocker.Mock(**td.JOB_AD)
    match = mocker.Mock(**td.MATCH)

    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = match

    # Act
    result = _get_match(
        job_application_id=job_application.id,
        job_ad_id=job_ad.id,
        db=mock_db,
    )

    # Assert
    assert_filter_called_with(
        mock_query,
        (Match.job_ad_id == td.VALID_JOB_AD_ID)
        & (Match.job_application_id == td.VALID_JOB_APPLICATION_ID),
    )
    assert result == match


def test_processRequestFromCompany_acceptsMatchRequest_whenValidData(
    mocker, mock_db
) -> None:
    # Arrange
    job_ad = mocker.Mock(**td.JOB_AD)
    job_application = mocker.Mock(**td.JOB_APPLICATION)
    match = mocker.Mock(**td.MATCH)

    mock_get_match = mocker.patch(
        "app.services.match_service._get_match",
        return_value=match,
    )
    mock_accept_match_request = mocker.patch(
        "app.services.match_service.accept_match_request",
        return_value={"msg": "Match Request accepted"},
    )

    accept_request = MatchResponseRequest(accept_request=True)

    # Act
    result = process_request_from_company(
        job_application_id=job_application.id,
        job_ad_id=job_ad.id,
        accept_request=accept_request,
        db=mock_db,
    )

    # Assert
    mock_get_match.assert_called_with(
        job_application_id=job_application.id, job_ad_id=job_ad.id, db=mock_db
    )
    mock_accept_match_request.assert_called_with(
        match=match,
        db=mock_db,
        job_application_id=job_application.id,
        job_ad_id=job_ad.id,
    )
    assert result == {"msg": "Match Request accepted"}


def test_processRequestFromCompany_rejectsMatchRequest_whenValidData(
    mocker, mock_db
) -> None:
    # Arrange
    job_ad = mocker.Mock(**td.JOB_AD)
    job_application = mocker.Mock(**td.JOB_APPLICATION)
    match = mocker.Mock(**td.MATCH)

    mock_get_match = mocker.patch(
        "app.services.match_service._get_match",
        return_value=match,
    )
    mock_reject_match_request = mocker.patch(
        "app.services.match_service.reject_match_request",
        return_value={"msg": "Match Request rejected"},
    )

    accept_request = MatchResponseRequest(accept_request=False)

    # Act
    result = process_request_from_company(
        job_application_id=job_application.id,
        job_ad_id=job_ad.id,
        accept_request=accept_request,
        db=mock_db,
    )

    # Assert
    mock_get_match.assert_called_with(
        job_application_id=job_application.id, job_ad_id=job_ad.id, db=mock_db
    )
    mock_reject_match_request.assert_called_with(
        match=match,
        db=mock_db,
        job_application_id=job_application.id,
        job_ad_id=job_ad.id,
    )
    assert result == {"msg": "Match Request rejected"}


def test_processRequestFromCompany_raisesError_whenNoExistingMatch(
    mocker, mock_db
) -> None:
    # Arrange
    job_ad = mocker.Mock(**td.JOB_AD)
    job_application = mocker.Mock(**td.JOB_APPLICATION)

    mock_get_match = mocker.patch(
        "app.services.match_service._get_match",
        return_value=None,
    )

    accept_request = MatchResponseRequest(accept_request=True)

    # Act & Assert
    with pytest.raises(ApplicationError) as exc:
        process_request_from_company(
            job_application_id=job_application.id,
            job_ad_id=job_ad.id,
            accept_request=accept_request,
            db=mock_db,
        )

    assert (
        exc.value.data.detail
        == f"No match found for JobApplication id{job_application.id} and JobAd id {job_ad.id}"
    )
    assert exc.value.data.status == status.HTTP_404_NOT_FOUND


def test_rejectMatchRequest_rejectsMatchRequest_whenValidData(mocker, mock_db) -> None:
    # Arrange
    job_ad = mocker.Mock(**td.JOB_AD)
    job_application = mocker.Mock(**td.JOB_APPLICATION)
    match = mocker.Mock(**td.MATCH)

    # Act
    result = reject_match_request(
        match=match,
        db=mock_db,
        job_application_id=job_application.id,
        job_ad_id=job_ad.id,
    )

    # Assert
    assert match.status == MatchStatus.REJECTED
    mock_db.commit.assert_called()
    assert isinstance(result, dict)
    assert result["msg"] == "Match Request rejected"


def test_acceptMatchRequest_acceptsMatchRequest_whenValidData(mocker, mock_db) -> None:
    # Arrange
    job_ad = mocker.Mock(**td.JOB_AD, status=JobAdStatus.ACTIVE)
    job_application = mocker.Mock(**td.JOB_APPLICATION)
    match = mocker.Mock(**td.MATCH, job_application=job_application, job_ad=job_ad)
    match.job_application.professional = mocker.Mock(
        active_application_count=1, status=ProfessionalStatus.ACTIVE
    )

    # Act
    result = accept_match_request(
        job_ad_id=job_ad.id,
        job_application_id=job_application.id,
        match=match,
        db=mock_db,
    )

    # Assert
    assert job_ad.status == JobAdStatus.ARCHIVED
    assert job_application.status == JobStatus.MATCHED
    assert match.status == MatchStatus.ACCEPTED
    assert match.job_application.professional.active_application_count == 0
    mock_db.commit.assert_called()
    assert result["msg"] == "Match Request accepted"


def test_getMatchRequestsForJobApplication_returnsMatchRequests_whenValidData(
    mocker, mock_db, mock_job_ads
) -> None:
    # Arrange
    filter_params = FilterParams(offset=0, limit=10)
    mock_job_ads[0].company = mocker.Mock()
    mock_job_ads[0].company.name = td.VALID_COMPANY_NAME
    mock_job_ads[1].company = mocker.Mock()
    mock_job_ads[1].company.name = td.VALID_COMPANY_NAME_2

    mock_query = mock_db.query.return_value
    mock_join = mock_query.join.return_value
    mock_filter = mock_join.filter.return_value
    mock_offset = mock_filter.offset.return_value
    mock_limit = mock_offset.limit.return_value
    mock_limit.all.return_value = [
        (mocker.Mock(**td.MATCH), mock_job_ads[0]),
        (mocker.Mock(**td.MATCH_2), mock_job_ads[1]),
    ]

    # Act
    result = get_match_requests_for_job_application(
        job_application_id=td.VALID_JOB_APPLICATION_ID,
        db=mock_db,
        filter_params=filter_params,
    )

    # Assert
    assert_filter_called_with(
        mock_join,
        (Match.job_application_id == td.VALID_JOB_APPLICATION_ID)
        & (Match.status == MatchStatus.REQUESTED_BY_JOB_AD),
    )
    mock_filter.offset.assert_called_with(filter_params.offset)
    mock_offset.limit.assert_called_with(filter_params.limit)
    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0], MatchRequestAd)
    assert isinstance(result[1], MatchRequestAd)


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


def test_sendJobApplicationMatchRequest_sendsMatchRequest_whenValidData(
    mocker, mock_db
) -> None:
    # Arrange
    job_ad = mocker.Mock(**td.JOB_AD)
    job_application = mocker.Mock(**td.JOB_APPLICATION)

    mock_ensure_valid_job_ad_id = mocker.patch(
        "app.services.match_service.ensure_valid_job_ad_id",
        return_value=job_ad,
    )
    mock_ensure_valid_job_application_id = mocker.patch(
        "app.services.match_service.ensure_valid_job_application_id",
        return_value=job_application,
    )
    mock_ensure_no_match_request = mocker.patch(
        "app.services.match_service.ensure_no_match_request",
    )

    # Act
    result = send_job_application_match_request(
        job_ad_id=job_ad.id,
        job_application_id=job_application.id,
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
    mock_ensure_no_match_request.assert_called_with(
        job_ad_id=job_ad.id,
        job_application_id=job_application.id,
        db=mock_db,
    )
    mock_db.add.assert_called()
    mock_db.commit.assert_called()
    assert isinstance(result, MessageResponse)


def test_viewReceivedJobApplicationMatchRequests_viewsMatchRequests_whenValidData(
    mocker, mock_db
) -> None:
    # Arrange
    job_ad = mocker.Mock(**td.JOB_AD)

    mock_query = mock_db.query.return_value
    mock_join = mock_query.join.return_value
    mock_filter = mock_join.filter.return_value
    mock_filter.all.return_value = [td.MATCH, td.MATCH_2]

    mock_ensure_valid_job_ad_id = mocker.patch(
        "app.services.match_service.ensure_valid_job_ad_id",
        return_value=job_ad,
    )
    mock_match_response_create = mocker.patch(
        "app.services.match_service.MatchResponse.create",
        side_effect=[
            MatchResponse(**td.MATCH),
            MatchResponse(**td.MATCH_2),
        ],
    )

    # Act
    result = view_received_job_application_match_requests(
        job_ad_id=job_ad.id,
        company_id=td.VALID_COMPANY_ID,
        db=mock_db,
    )

    # Assert
    mock_ensure_valid_job_ad_id.assert_called_with(
        job_ad_id=job_ad.id,
        db=mock_db,
        company_id=job_ad.company_id,
    )
    assert_filter_called_with(
        mock_join,
        (JobAd.id == str(job_ad.id))
        & (Match.status == MatchStatus.REQUESTED_BY_JOB_APP),
    )
    mock_match_response_create.assert_has_calls([call(td.MATCH), call(td.MATCH_2)])
    assert isinstance(result, list)
    assert isinstance(result[0], MatchResponse)
    assert isinstance(result[1], MatchResponse)
    assert len(result) == 2


def test_viewSentJobApplicationMatchRequests_viewsSentMatchRequests_whenValidData(
    mocker, mock_db
) -> None:
    # Arrange
    job_ad = mocker.Mock(**td.JOB_AD)

    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.all.return_value = [td.MATCH, td.MATCH_2]

    mock_ensure_valid_job_ad_id = mocker.patch(
        "app.services.match_service.ensure_valid_job_ad_id",
        return_value=job_ad,
    )
    mock_match_response_create = mocker.patch(
        "app.services.match_service.MatchResponse.create",
        side_effect=[
            MatchResponse(**td.MATCH),
            MatchResponse(**td.MATCH_2),
        ],
    )

    # Act
    result = view_sent_job_application_match_requests(
        job_ad_id=job_ad.id,
        company_id=job_ad.company_id,
        db=mock_db,
    )

    # Assert
    mock_ensure_valid_job_ad_id.assert_called_with(
        job_ad_id=job_ad.id,
        db=mock_db,
        company_id=job_ad.company_id,
    )
    assert_filter_called_with(
        mock_query,
        (Match.job_ad_id == str(job_ad.id))
        & (Match.status == MatchStatus.REQUESTED_BY_JOB_AD),
    )
    mock_match_response_create.assert_has_calls([call(td.MATCH), call(td.MATCH_2)])
    assert isinstance(result, list)
    assert isinstance(result[0], MatchResponse)
    assert isinstance(result[1], MatchResponse)
    assert len(result) == 2


def test_getCompanyMatchRequests_returnsMatchRequests_whenValidData(
    mocker, mock_db, mock_job_ads
) -> None:
    # Arrange
    filter_params = FilterParams(offset=0, limit=10)

    mock_query = mock_db.query.return_value
    mock_join = mock_query.join.return_value
    mock_filter = mock_join.filter.return_value
    mock_offset = mock_filter.offset.return_value
    mock_limit = mock_offset.limit.return_value
    mock_limit.all.return_value = [
        mocker.Mock(**td.MATCH, job_ad=mock_job_ads[0]),
        mocker.Mock(**td.MATCH_2, job_ad=mock_job_ads[1]),
    ]

    # Act
    result = get_company_match_requests(
        company_id=td.VALID_COMPANY_ID,
        db=mock_db,
        filter_params=filter_params,
    )

    # Assert
    mock_db.query.assert_called_with(Match)
    mock_query.join.assert_called_with(Match.job_ad)
    assert_filter_called_with(
        mock_join,
        (JobAd.company_id == td.VALID_COMPANY_ID)
        & (Match.status == MatchStatus.REQUESTED_BY_JOB_APP),
    )
    mock_filter.offset.assert_called_with(filter_params.offset)
    mock_offset.limit.assert_called_with(filter_params.limit)
    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0], MatchResponse)
    assert isinstance(result[1], MatchResponse)
