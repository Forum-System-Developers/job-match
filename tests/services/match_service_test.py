import pytest
from fastapi import status

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.common import FilterParams, MessageResponse
from app.services import match_service
from app.services.enums.match_status import MatchStatus
from app.services.external_db_service_urls import (
    MATCH_REQUESTS_BY_ID_URL,
    MATCH_REQUESTS_JOB_APPLICATIONS_URL,
    MATCH_REQUESTS_PROFESSIONALS_URL,
    MATCH_REQUESTS_URL,
)
from tests import test_data as td


def test_createIfNotExists_createsMatchRequest_whenNoExistingMatch(mocker) -> None:
    # Arrange
    job_application_id = td.VALID_JOB_APPLICATION_ID
    job_ad_id = td.VALID_JOB_AD_ID
    mock_match_create = mocker.MagicMock()

    mock_get_match_request_by_id = mocker.patch(
        "app.services.match_service.get_match_request_by_id",
        return_value=None,
    )
    mocker_match_request_create = mocker.patch(
        "app.services.match_service.MatchRequestCreate", return_value=mock_match_create
    )
    mock_perform_post_request = mocker.patch(
        "app.services.match_service.perform_post_request",
    )

    # Act
    result = match_service.create_if_not_exists(
        job_application_id=job_application_id,
        job_ad_id=job_ad_id,
    )

    # Assert
    mock_get_match_request_by_id.assert_called_with(
        job_application_id=job_application_id,
        job_ad_id=job_ad_id,
    )
    mock_perform_post_request.assert_called_with(
        url=MATCH_REQUESTS_URL,
        json={**mock_match_create},
    )
    assert isinstance(result, MessageResponse)
    assert result.message == "Match Request successfully sent"


def test_createIfNotExists_raisesError_whenMatchRequestedByJobApp(mocker) -> None:
    # Arrange
    job_application_id = td.VALID_JOB_APPLICATION_ID
    job_ad_id = td.VALID_JOB_AD_ID
    existing_match = mocker.Mock(status=MatchStatus.REQUESTED_BY_JOB_APP)

    mock_get_match_request_by_id = mocker.patch(
        "app.services.match_service.get_match_request_by_id",
        return_value=existing_match,
    )

    # Act & Assert
    with pytest.raises(ApplicationError) as exc:
        match_service.create_if_not_exists(
            job_application_id=job_application_id,
            job_ad_id=job_ad_id,
        )

    assert exc.value.data.detail == "Match Request already sent"
    assert exc.value.data.status == status.HTTP_403_FORBIDDEN
    mock_get_match_request_by_id.assert_called_with(
        job_application_id=job_application_id,
        job_ad_id=job_ad_id,
    )


def test_createIfNotExists_raisesError_whenMatchRequestedByJobAd(mocker) -> None:
    # Arrange
    job_application_id = td.VALID_JOB_APPLICATION_ID
    job_ad_id = td.VALID_JOB_AD_ID
    existing_match = mocker.Mock(status=MatchStatus.REQUESTED_BY_JOB_AD)

    mock_get_match_request_by_id = mocker.patch(
        "app.services.match_service.get_match_request_by_id",
        return_value=existing_match,
    )

    # Act & Assert
    with pytest.raises(ApplicationError) as exc:
        match_service.create_if_not_exists(
            job_application_id=job_application_id,
            job_ad_id=job_ad_id,
        )

    assert exc.value.data.detail == "Match Request already sent"
    assert exc.value.data.status == status.HTTP_403_FORBIDDEN
    mock_get_match_request_by_id.assert_called_with(
        job_application_id=job_application_id,
        job_ad_id=job_ad_id,
    )


def test_createIfNotExists_raisesError_whenMatchAccepted(mocker) -> None:
    # Arrange
    job_application_id = td.VALID_JOB_APPLICATION_ID
    job_ad_id = td.VALID_JOB_AD_ID
    existing_match = mocker.Mock(status=MatchStatus.ACCEPTED)

    mock_get_match_request_by_id = mocker.patch(
        "app.services.match_service.get_match_request_by_id",
        return_value=existing_match,
    )

    # Act & Assert
    with pytest.raises(ApplicationError) as exc:
        match_service.create_if_not_exists(
            job_application_id=job_application_id,
            job_ad_id=job_ad_id,
        )

    assert exc.value.data.detail == "Match Request already accepted"
    assert exc.value.data.status == status.HTTP_403_FORBIDDEN
    mock_get_match_request_by_id.assert_called_with(
        job_application_id=job_application_id,
        job_ad_id=job_ad_id,
    )


def test_createIfNotExists_raisesError_whenMatchRejected(mocker) -> None:
    # Arrange
    job_application_id = td.VALID_JOB_APPLICATION_ID
    job_ad_id = td.VALID_JOB_AD_ID
    existing_match = mocker.Mock(status=MatchStatus.REJECTED)

    mock_get_match_request_by_id = mocker.patch(
        "app.services.match_service.get_match_request_by_id",
        return_value=existing_match,
    )

    # Act & Assert
    with pytest.raises(ApplicationError) as exc:
        match_service.create_if_not_exists(
            job_application_id=job_application_id,
            job_ad_id=job_ad_id,
        )

    assert (
        exc.value.data.detail
        == "Match Request was rejested, cannot create a new Match request"
    )
    assert exc.value.data.status == status.HTTP_403_FORBIDDEN
    mock_get_match_request_by_id.assert_called_with(
        job_application_id=job_application_id,
        job_ad_id=job_ad_id,
    )


def test_processRequestFromCompany_acceptsRequest_whenMatchExists(mocker) -> None:
    # Arrange
    job_application_id = td.VALID_JOB_APPLICATION_ID
    job_ad_id = td.VALID_JOB_AD_ID
    mock_accept_request = mocker.Mock(accept_request=True)
    mock_existing_match = mocker.Mock()

    mock_get_match_request_by_id = mocker.patch(
        "app.services.match_service.get_match_request_by_id",
        return_value=mock_existing_match,
    )
    mock_accept_match_request = mocker.patch(
        "app.services.match_service.accept_match_request",
        return_value=MessageResponse(message="Match Request accepted"),
    )

    # Act
    result = match_service.process_request_from_company(
        job_application_id=job_application_id,
        job_ad_id=job_ad_id,
        accept_request=mock_accept_request,
    )

    # Assert
    mock_get_match_request_by_id.assert_called_with(
        job_application_id=job_application_id,
        job_ad_id=job_ad_id,
    )
    mock_accept_match_request.assert_called_with(
        job_application_id=job_application_id,
        job_ad_id=job_ad_id,
    )
    assert isinstance(result, MessageResponse)
    assert result.message == "Match Request accepted"


def test_processRequestFromCompany_rejectsRequest_whenMatchExists(mocker) -> None:
    # Arrange
    job_application_id = td.VALID_JOB_APPLICATION_ID
    job_ad_id = td.VALID_JOB_AD_ID
    mock_accept_request = mocker.Mock(accept_request=False)
    mock_existing_match = mocker.Mock()

    mock_get_match_request_by_id = mocker.patch(
        "app.services.match_service.get_match_request_by_id",
        return_value=mock_existing_match,
    )
    mock_reject_match_request = mocker.patch(
        "app.services.match_service.reject_match_request",
        return_value=MessageResponse(message="Match Request rejected"),
    )

    # Act
    result = match_service.process_request_from_company(
        job_application_id=job_application_id,
        job_ad_id=job_ad_id,
        accept_request=mock_accept_request,
    )

    # Assert
    mock_get_match_request_by_id.assert_called_with(
        job_application_id=job_application_id,
        job_ad_id=job_ad_id,
    )
    mock_reject_match_request.assert_called_with(
        job_application_id=job_application_id,
        job_ad_id=job_ad_id,
    )
    assert isinstance(result, MessageResponse)
    assert result.message == "Match Request rejected"


def test_processRequestFromCompany_raisesError_whenNoMatchExists(mocker) -> None:
    # Arrange
    job_application_id = td.VALID_JOB_APPLICATION_ID
    job_ad_id = td.VALID_JOB_AD_ID
    accept_request = mocker.Mock()

    mock_get_match_request_by_id = mocker.patch(
        "app.services.match_service.get_match_request_by_id",
        return_value=None,
    )

    # Act & Assert
    with pytest.raises(ApplicationError) as exc:
        match_service.process_request_from_company(
            job_application_id=job_application_id,
            job_ad_id=job_ad_id,
            accept_request=accept_request,
        )

    assert (
        exc.value.data.detail
        == f"No match found for JobApplication id{job_application_id} and JobAd id {job_ad_id}"
    )
    assert exc.value.data.status == status.HTTP_404_NOT_FOUND
    mock_get_match_request_by_id.assert_called_with(
        job_application_id=job_application_id,
        job_ad_id=job_ad_id,
    )


def test_rejectMatchRequest_rejectsRequestSuccessfully(mocker) -> None:
    # Arrange
    job_application_id = td.VALID_JOB_APPLICATION_ID
    job_ad_id = td.VALID_JOB_AD_ID

    mock_perform_patch_request = mocker.patch(
        "app.services.match_service.perform_patch_request",
    )

    # Act
    result = match_service.reject_match_request(
        job_application_id=job_application_id,
        job_ad_id=job_ad_id,
    )

    # Assert
    mock_perform_patch_request.assert_called_with(
        url=MATCH_REQUESTS_BY_ID_URL.format(
            job_ad_id=job_ad_id, job_application_id=job_application_id
        ),
        json={"status": MatchStatus.REJECTED},
    )
    assert isinstance(result, MessageResponse)
    assert result.message == "Match Request rejected"


def test_acceptMatchRequest_acceptsRequestSuccessfully(mocker) -> None:
    # Arrange
    job_application_id = td.VALID_JOB_APPLICATION_ID
    job_ad_id = td.VALID_JOB_AD_ID

    mock_perform_put_request = mocker.patch(
        "app.services.match_service.perform_put_request",
    )

    # Act
    result = match_service.accept_match_request(
        job_application_id=job_application_id,
        job_ad_id=job_ad_id,
    )

    # Assert
    mock_perform_put_request.assert_called_with(
        url=MATCH_REQUESTS_BY_ID_URL.format(
            job_ad_id=job_ad_id, job_application_id=job_application_id
        ),
    )
    assert isinstance(result, MessageResponse)
    assert result.message == "Match Request accepted"


def test_getMatchRequestsForJobApplication_returnsRequests(mocker) -> None:
    # Arrange
    job_application_id = td.VALID_JOB_APPLICATION_ID
    filter_params = mocker.Mock(limit=10, offset=0)
    mock_requests = [mocker.MagicMock(), mocker.MagicMock()]

    mock_perform_get_request = mocker.patch(
        "app.services.match_service.perform_get_request",
        return_value=mock_requests,
    )
    mock_match_request_ad = mocker.patch(
        "app.services.match_service.MatchRequestAd",
    )

    # Act
    result = match_service.get_match_requests_for_job_application(
        job_application_id=job_application_id,
        filter_params=filter_params,
    )

    # Assert
    mock_perform_get_request.assert_called_with(
        url=MATCH_REQUESTS_JOB_APPLICATIONS_URL.format(
            job_application_id=job_application_id
        ),
        params=filter_params.model_dump(),
    )
    assert isinstance(result, list)
    assert len(result) == 2


def test_getMatchRequestsForJobApplication_returnsEmptyList_whenNoRequests(
    mocker,
) -> None:
    # Arrange
    job_application_id = td.VALID_JOB_APPLICATION_ID
    filter_params = FilterParams(limit=10, offset=0)

    mock_perform_get_request = mocker.patch(
        "app.services.match_service.perform_get_request",
        return_value=[],
    )

    # Act
    result = match_service.get_match_requests_for_job_application(
        job_application_id=job_application_id,
        filter_params=filter_params,
    )

    # Assert
    mock_perform_get_request.assert_called_with(
        url=MATCH_REQUESTS_JOB_APPLICATIONS_URL.format(
            job_application_id=job_application_id
        ),
        params=filter_params.model_dump(),
    )
    assert result == []


def test_getMatchRequestsForProfessional_returnsRequests(mocker) -> None:
    # Arrange
    professional_id = td.VALID_PROFESSIONAL_ID
    mock_requests = [mocker.MagicMock(), mocker.MagicMock()]

    mock_perform_get_request = mocker.patch(
        "app.services.match_service.perform_get_request",
        return_value=mock_requests,
    )
    mock_match_request_ad = mocker.patch(
        "app.services.match_service.MatchRequestAd",
    )

    # Act
    result = match_service.get_match_requests_for_professional(
        professional_id=professional_id,
    )

    # Assert
    mock_perform_get_request.assert_called_with(
        url=MATCH_REQUESTS_PROFESSIONALS_URL.format(professional_id=professional_id)
    )
    assert isinstance(result, list)
    assert len(result) == 2


def test_getMatchRequestsForProfessional_returnsEmptyList_whenNoRequests(
    mocker,
) -> None:
    # Arrange
    professional_id = td.VALID_PROFESSIONAL_ID

    mock_perform_get_request = mocker.patch(
        "app.services.match_service.perform_get_request",
        return_value=[],
    )

    # Act
    result = match_service.get_match_requests_for_professional(
        professional_id=professional_id,
    )

    # Assert
    mock_perform_get_request.assert_called_with(
        url=MATCH_REQUESTS_PROFESSIONALS_URL.format(professional_id=professional_id)
    )
    assert result == []


def test_acceptJobApplicationMatchRequest_acceptsRequestSuccessfully(mocker) -> None:
    # Arrange
    job_application_id = td.VALID_JOB_APPLICATION_ID
    job_ad_id = td.VALID_JOB_AD_ID
    company_id = td.VALID_COMPANY_ID

    mock_accept_match_request = mocker.patch(
        "app.services.match_service.accept_match_request",
        return_value=MessageResponse(message="Match Request accepted"),
    )
    mock_ensure_valid_job_ad_id = mocker.patch(
        "app.services.match_service.ensure_valid_job_ad_id",
    )

    # Act
    result = match_service.accept_job_application_match_request(
        job_ad_id=job_ad_id,
        job_application_id=job_application_id,
        company_id=company_id,
    )

    # Assert
    mock_ensure_valid_job_ad_id.assert_called_with(
        job_ad_id=job_ad_id, company_id=company_id
    )
    mock_accept_match_request.assert_called_with(
        job_ad_id=job_ad_id,
        job_application_id=job_application_id,
    )
    assert isinstance(result, MessageResponse)
    assert result.message == "Match Request accepted"


def test_acceptJobApplicationMatchRequest_raisesError_whenInvalidJobAdId(
    mocker,
) -> None:
    # Arrange
    job_application_id = td.VALID_JOB_APPLICATION_ID
    job_ad_id = td.NON_EXISTENT_ID
    company_id = td.VALID_COMPANY_ID

    mock_ensure_valid_job_ad_id = mocker.patch(
        "app.services.match_service.ensure_valid_job_ad_id",
        side_effect=ApplicationError(
            detail="Invalid Job Ad ID",
            status_code=status.HTTP_400_BAD_REQUEST,
        ),
    )

    # Act & Assert
    with pytest.raises(ApplicationError) as exc:
        match_service.accept_job_application_match_request(
            job_ad_id=job_ad_id,
            job_application_id=job_application_id,
            company_id=company_id,
        )

    assert exc.value.data.detail == "Invalid Job Ad ID"
    assert exc.value.data.status == status.HTTP_400_BAD_REQUEST
    mock_ensure_valid_job_ad_id.assert_called_with(
        job_ad_id=job_ad_id, company_id=company_id
    )
