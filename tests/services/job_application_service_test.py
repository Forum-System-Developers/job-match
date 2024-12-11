import pytest

from app.services import job_application_service
from tests import test_data as td


def test_getAllJobApplications_returnsJobApplications_whenJobApplicationsAreFound(
    mocker,
) -> None:
    # Arrange
    filter_params = mocker.Mock()
    filter_params.model_dump = mocker.Mock(return_value={"offset": 0, "limit": 10})
    search_params = mocker.Mock()
    search_params.model_dump = mocker.Mock(
        return_value={
            "order": "asc",
            "order_by": "created_at",
            "skills": ["Python", "Linux", "React"],
        }
    )
    job_applications = [td.JOB_APPLICATION, td.JOB_APPLICATION_2]

    mock_perform_post_request = mocker.patch(
        "app.services.job_application_service.perform_post_request",
        return_value=job_applications,
    )
    mock_job_app_response = mocker.patch(
        "app.services.job_application_service.JobApplicationResponse",
        side_effect=job_applications,
    )

    # Act
    result = job_application_service.get_all(
        filter_params=filter_params,
        search_params=search_params,
    )

    # Assert
    mock_perform_post_request.assert_called_once_with(
        url=job_application_service.JOB_APPLICATIONS_ALL_URL,
        params={
            **search_params.model_dump(mode="json"),
            **filter_params.model_dump(mode="json"),
        },
    )
    assert len(result) == len(job_applications)
    assert result == job_applications


def test_getAllJobApplications_returnsEmptyList_whenNoJobApplicationsAreFound(
    mocker,
) -> None:
    # Arrange
    filter_params = mocker.Mock()
    filter_params.model_dump = mocker.Mock(return_value={"offset": 0, "limit": 10})
    search_params = mocker.Mock()
    search_params.model_dump = mocker.Mock(
        return_value={
            "order": "asc",
            "order_by": "created_at",
            "skills": ["Python", "Linux", "React"],
        }
    )

    mock_perform_post_request = mocker.patch(
        "app.services.job_application_service.perform_post_request",
        return_value=[],
    )

    # Act
    result = job_application_service.get_all(
        filter_params=filter_params,
        search_params=search_params,
    )

    # Assert
    mock_perform_post_request.assert_called_once_with(
        url=job_application_service.JOB_APPLICATIONS_ALL_URL,
        params={
            **search_params.model_dump(mode="json"),
            **filter_params.model_dump(mode="json"),
        },
    )
    assert result == []


def test_create_returnsJobApplicationResponse_whenDataIsValid(mocker) -> None:
    # Arrange
    job_application = td.JOB_APPLICATION
    mock_job_application_data = mocker.Mock(city="City")
    mock_job_application_final_data = mocker.Mock()
    mock_response = mocker.Mock()

    mock_get_by_name = mocker.patch(
        "app.services.city_service.get_by_name",
        return_value=mocker.Mock(**td.CITY),
    )
    mock_job_app_final_response = mocker.patch(
        "app.services.job_application_service.JobApplicationCreateFinal",
        return_value=mock_job_application_final_data,
    )
    mock_perform_post_request = mocker.patch(
        "app.services.job_application_service.perform_post_request",
        return_value=job_application,
    )
    mock_job_app_response = mocker.patch(
        "app.services.job_application_service.JobApplicationResponse",
        return_value=mock_response,
    )

    # Act
    result = job_application_service.create(
        professional_id=td.VALID_PROFESSIONAL_ID,
        job_application_data=mock_job_application_data,
    )

    # Assert
    mock_get_by_name.assert_called_once_with(city_name=mock_job_application_data.city)
    mock_perform_post_request.assert_called_once_with(
        url=job_application_service.JOB_APPLICATIONS_URL,
        json=mocker.ANY,
    )
    mock_job_app_final_response.create.assert_called_once_with(
        job_application_create=mock_job_application_data,
        city_id=td.CITY["id"],
        professional_id=td.VALID_PROFESSIONAL_ID,
    )
    mock_job_app_response.assert_called_once_with(**job_application)
    assert result == mock_response


def test_update_returnsUpdatedJobApplicationResponse_whenDataIsValid(mocker) -> None:
    # Arrange
    job_application_id = td.VALID_JOB_APPLICATION_ID
    professional_id = td.VALID_PROFESSIONAL_ID
    mock_job_application_update = mocker.Mock()
    mock_job_application_final_data = mocker.Mock()
    mock_updated_job_application = mocker.MagicMock()
    mock_response = mocker.Mock()

    mock_ensure_valid_job_application_id = mocker.patch(
        "app.services.job_application_service.ensure_valid_job_application_id"
    )
    mock_prepare_job_application_update_final_data = mocker.patch(
        "app.services.job_application_service._prepare_job_application_update_final_data",
        return_value=mock_job_application_final_data,
    )
    mock_perform_put_request = mocker.patch(
        "app.services.job_application_service.perform_put_request",
        return_value=mock_updated_job_application,
    )
    mock_job_app_response = mocker.patch(
        "app.services.job_application_service.JobApplicationResponse",
        return_value=mock_response,
    )

    # Act
    result = job_application_service.update(
        job_application_id=job_application_id,
        job_application_update=mock_job_application_update,
        professional_id=professional_id,
    )

    # Assert
    mock_ensure_valid_job_application_id.assert_called_once_with(
        job_application_id=job_application_id,
        professional_id=professional_id,
    )
    mock_prepare_job_application_update_final_data.assert_called_once_with(
        job_application_update=mock_job_application_update,
    )
    mock_perform_put_request.assert_called_once_with(
        url=job_application_service.JOB_APPLICATIONS_BY_ID_URL.format(
            job_application_id=job_application_id
        ),
        json=mock_job_application_final_data.model_dump(mode="json"),
    )
    mock_job_app_response.assert_called_once_with(**mock_updated_job_application)
    assert result == mock_response


def test_getById_returnsJobApplicationResponse_whenJobApplicationIsFound(
    mocker,
) -> None:
    # Arrange
    job_application_id = td.VALID_JOB_APPLICATION_ID
    mock_job_application = mocker.MagicMock()
    mock_response = mocker.Mock()

    mock_perform_get_request = mocker.patch(
        "app.services.job_application_service.perform_get_request",
        return_value=mock_job_application,
    )
    mock_job_app_response = mocker.patch(
        "app.services.job_application_service.JobApplicationResponse",
        return_value=mock_response,
    )

    # Act
    result = job_application_service.get_by_id(job_application_id=job_application_id)

    # Assert
    mock_perform_get_request.assert_called_once_with(
        url=job_application_service.JOB_APPLICATIONS_BY_ID_URL.format(
            job_application_id=job_application_id
        ),
    )
    mock_job_app_response.assert_called_once_with(**mock_job_application)
    assert result == mock_response


def test_requestMatch_createsMatchRequest_whenDataIsValid(mocker) -> None:
    # Arrange
    job_application_id = td.VALID_JOB_APPLICATION_ID
    job_ad_id = td.VALID_JOB_AD_ID
    mock_message_response = mocker.Mock()

    mock_ensure_valid_job_application_id = mocker.patch(
        "app.services.job_application_service.ensure_valid_job_application_id"
    )
    mock_ensure_valid_job_ad_id = mocker.patch(
        "app.services.job_application_service.ensure_valid_job_ad_id"
    )
    mock_create_if_not_exists = mocker.patch(
        "app.services.match_service.create_if_not_exists",
        return_value=mock_message_response,
    )

    # Act
    result = job_application_service.request_match(
        job_application_id=job_application_id,
        job_ad_id=job_ad_id,
    )

    # Assert
    mock_ensure_valid_job_application_id.assert_called_once_with(
        job_application_id=job_application_id
    )
    mock_ensure_valid_job_ad_id.assert_called_once_with(job_ad_id=job_ad_id)
    mock_create_if_not_exists.assert_called_once_with(
        job_application_id=job_application_id,
        job_ad_id=job_ad_id,
    )
    assert result == mock_message_response


def test_handleMatchResponse_acceptsMatchRequest_whenDataIsValid(mocker) -> None:
    # Arrange
    job_application_id = td.VALID_JOB_APPLICATION_ID
    job_ad_id = td.VALID_JOB_AD_ID
    mock_accept_request = mocker.Mock()
    mock_message_response = mocker.Mock()

    mock_ensure_valid_job_application_id = mocker.patch(
        "app.services.job_application_service.ensure_valid_job_application_id"
    )
    mock_ensure_valid_job_ad_id = mocker.patch(
        "app.services.job_application_service.ensure_valid_job_ad_id"
    )
    mock_process_request_from_company = mocker.patch(
        "app.services.match_service.process_request_from_company",
        return_value=mock_message_response,
    )

    # Act
    result = job_application_service.handle_match_response(
        job_application_id=job_application_id,
        job_ad_id=job_ad_id,
        accept_request=mock_accept_request,
    )

    # Assert
    mock_ensure_valid_job_application_id.assert_called_once_with(
        job_application_id=job_application_id
    )
    mock_ensure_valid_job_ad_id.assert_called_once_with(job_ad_id=job_ad_id)
    mock_process_request_from_company.assert_called_once_with(
        job_application_id=job_application_id,
        job_ad_id=job_ad_id,
        accept_request=mock_accept_request,
    )
    assert result == mock_message_response


def test_viewMatchRequests_returnsMatchRequests_whenMatchRequestsAreFound(
    mocker,
) -> None:
    # Arrange
    job_application_id = td.VALID_JOB_APPLICATION_ID
    mock_filter_params = mocker.Mock()
    mock_filter_params.model_dump = mocker.Mock(return_value={"offset": 0, "limit": 10})
    mock_match_requests = [mocker.Mock(), mocker.Mock()]

    mock_ensure_valid_job_application_id = mocker.patch(
        "app.services.job_application_service.ensure_valid_job_application_id"
    )
    mock_get_match_requests_for_job_application = mocker.patch(
        "app.services.match_service.get_match_requests_for_job_application",
        return_value=mock_match_requests,
    )

    # Act
    result = job_application_service.view_match_requests(
        job_application_id=job_application_id,
        filter_params=mock_filter_params,
    )

    # Assert
    mock_ensure_valid_job_application_id.assert_called_once_with(
        job_application_id=job_application_id
    )
    mock_get_match_requests_for_job_application.assert_called_once_with(
        job_application_id=job_application_id,
        filter_params=mock_filter_params,
    )
    assert len(result) == len(mock_match_requests)
    assert result == mock_match_requests


def test_prepareJobApplicationUpdateFinalData_returnsFinalData_whenCityIsNone(
    mocker,
) -> None:
    # Arrange
    job_application_update = mocker.Mock(city=None)
    mock_job_application_final_data = mocker.Mock()

    mock_create_final_data = mocker.patch(
        "app.services.job_application_service.JobApplicationUpdateFinal.create",
        return_value=mock_job_application_final_data,
    )

    # Act
    result = job_application_service._prepare_job_application_update_final_data(
        job_application_update=job_application_update,
    )

    # Assert
    mock_create_final_data.assert_called_once_with(
        job_application_update=job_application_update,
    )
    assert result == mock_job_application_final_data


def test_prepareJobApplicationUpdateFinalData_returnsFinalDataWithCityId_whenCityIsNotNone(
    mocker,
) -> None:
    # Arrange
    job_application_update = mocker.Mock(city="City")
    mock_job_application_final_data = mocker.Mock()
    mock_city = mocker.Mock(id=1)

    mock_create_final_data = mocker.patch(
        "app.services.job_application_service.JobApplicationUpdateFinal.create",
        return_value=mock_job_application_final_data,
    )
    mock_ensure_valid_city = mocker.patch(
        "app.services.job_application_service.ensure_valid_city",
        return_value=mock_city,
    )

    # Act
    result = job_application_service._prepare_job_application_update_final_data(
        job_application_update=job_application_update,
    )

    # Assert
    mock_create_final_data.assert_called_once_with(
        job_application_update=job_application_update,
    )
    mock_ensure_valid_city.assert_called_once_with(name=job_application_update.city)
    assert result == mock_job_application_final_data
    assert result.city_id == mock_city.id
