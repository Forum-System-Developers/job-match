import pytest

from app.schemas.common import MessageResponse
from app.schemas.job_ad import JobAdCreate, JobAdCreateFull, JobAdResponse, JobAdUpdate
from app.services import job_ad_service
from app.services.external_db_service_urls import (
    JOB_AD_ADD_SKILL_URL,
    JOB_AD_BY_ID_URL,
    JOB_ADS_URL,
)
from tests import test_data as td


def test_getAll_returnsJobAds_whenJobAdsExist(mocker) -> None:
    # Arrange
    filter_params = mocker.Mock(offset=0, limit=10)
    search_params = mocker.Mock()
    job_ads = [td.JOB_AD, td.JOB_AD_2]
    job_ad_responses = [
        mocker.Mock(spec=JobAdResponse),
        mocker.Mock(spec=JobAdResponse),
    ]

    mock_perform_post_request = mocker.patch(
        "app.services.job_ad_service.perform_post_request",
        return_value=job_ads,
    )
    mock_job_ad_response = mocker.patch(
        "app.services.job_ad_service.JobAdResponse",
        side_effect=job_ad_responses,
    )

    # Act
    result = job_ad_service.get_all(filter_params, search_params)

    # Assert
    mock_perform_post_request.assert_called_once_with(
        url=f"{JOB_ADS_URL}/all",
        json=search_params.model_dump(mode="json"),
        params=filter_params.model_dump(),
    )
    assert len(result) == 2
    assert result == job_ad_responses


def test_getAll_returnsEmptyList_whenNoJobAdsExist(mocker) -> None:
    # Arrange
    filter_params = mocker.Mock(offset=0, limit=10)
    search_params = mocker.Mock()

    mock_perform_post_request = mocker.patch(
        "app.services.job_ad_service.perform_post_request",
        return_value=[],
    )

    # Act
    result = job_ad_service.get_all(filter_params, search_params)

    # Assert
    mock_perform_post_request.assert_called_once_with(
        url=f"{JOB_ADS_URL}/all",
        json=search_params.model_dump(mode="json"),
        params=filter_params.model_dump(),
    )
    assert result == []


def test_getById_returnsJobAd_whenJobAdExists(mocker) -> None:
    # Arrange
    job_ad_id = td.VALID_JOB_AD_ID
    job_ad_response = mocker.Mock(spec=JobAdResponse)

    mock_perform_get_request = mocker.patch(
        "app.services.job_ad_service.perform_get_request",
        return_value=td.JOB_AD,
    )
    mock_job_ad_response = mocker.patch(
        "app.services.job_ad_service.JobAdResponse",
        return_value=job_ad_response,
    )

    # Act
    result = job_ad_service.get_by_id(job_ad_id)

    # Assert
    mock_perform_get_request.assert_called_once_with(
        url=f"{JOB_AD_BY_ID_URL.format(job_ad_id=job_ad_id)}"
    )
    mock_job_ad_response.assert_called_once_with(**td.JOB_AD)
    assert result == job_ad_response


def test_getById_raisesException_whenJobAdDoesNotExist(mocker) -> None:
    # Arrange
    job_ad_id = td.VALID_JOB_AD_ID

    mock_perform_get_request = mocker.patch(
        "app.services.job_ad_service.perform_get_request",
        side_effect=Exception("Job ad not found"),
    )

    # Act & Assert
    with pytest.raises(Exception, match="Job ad not found"):
        job_ad_service.get_by_id(job_ad_id)

    mock_perform_get_request.assert_called_once_with(
        url=f"{JOB_AD_BY_ID_URL.format(job_ad_id=job_ad_id)}"
    )


def test_create_returnsJobAd_whenDataIsValid(mocker) -> None:
    # Arrange
    company_id = td.VALID_COMPANY_ID
    job_ad_data = mocker.Mock(spec=JobAdCreate)
    job_ad_data.model_dump.return_value = {}
    job_ad_full_data = mocker.Mock(spec=JobAdCreateFull)
    job_ad_response = mocker.Mock(spec=JobAdResponse)

    mock_job_ad_create_full = mocker.patch(
        "app.services.job_ad_service.JobAdCreateFull",
        return_value=job_ad_full_data,
    )
    mock_perform_post_request = mocker.patch(
        "app.services.job_ad_service.perform_post_request",
        return_value=td.JOB_AD,
    )
    mock_job_ad_response = mocker.patch(
        "app.services.job_ad_service.JobAdResponse",
        return_value=job_ad_response,
    )

    # Act
    result = job_ad_service.create(company_id, job_ad_data)

    # Assert
    mock_job_ad_create_full.assert_called_once_with(
        **job_ad_data.model_dump(), company_id=company_id
    )
    mock_perform_post_request.assert_called_once_with(
        url=JOB_ADS_URL,
        json=job_ad_full_data.model_dump(mode="json"),
    )
    mock_job_ad_response.assert_called_once_with(**td.JOB_AD)
    assert result == job_ad_response


def test_update_returnsUpdatedJobAd_whenLocationIsNone(mocker) -> None:
    # Arrange
    job_ad_id = td.VALID_JOB_AD_ID
    company_id = td.VALID_COMPANY_ID
    job_ad_data = mocker.Mock(spec=JobAdUpdate, location=None)
    job_ad_response = mocker.Mock(spec=JobAdResponse)

    mock_ensure_valid_job_ad_id = mocker.patch(
        "app.services.job_ad_service.ensure_valid_job_ad_id"
    )
    mock_ensure_valid_city = mocker.patch(
        "app.services.job_ad_service.ensure_valid_city"
    )
    mock_perform_put_request = mocker.patch(
        "app.services.job_ad_service.perform_put_request",
        return_value=td.JOB_AD,
    )
    mock_job_ad_response = mocker.patch(
        "app.services.job_ad_service.JobAdResponse",
        return_value=job_ad_response,
    )

    # Act
    result = job_ad_service.update(job_ad_id, company_id, job_ad_data)

    # Assert
    mock_ensure_valid_job_ad_id.assert_called_once_with(
        job_ad_id=job_ad_id, company_id=company_id
    )
    mock_ensure_valid_city.assert_not_called()
    mock_perform_put_request.assert_called_once_with(
        url=f"{JOB_AD_BY_ID_URL.format(job_ad_id=job_ad_id)}",
        json=job_ad_data.model_dump(mode="json"),
    )
    mock_job_ad_response.assert_called_once_with(**td.JOB_AD)
    assert result == job_ad_response


def test_update_returnsUpdatedJobAd_whenLocationIsNotNone(mocker) -> None:
    # Arrange
    job_ad_id = td.VALID_JOB_AD_ID
    company_id = td.VALID_COMPANY_ID
    job_ad_data = mocker.Mock(spec=JobAdUpdate, location=td.VALID_CITY_NAME)
    job_ad_response = mocker.Mock(spec=JobAdResponse)

    mock_ensure_valid_job_ad_id = mocker.patch(
        "app.services.job_ad_service.ensure_valid_job_ad_id"
    )
    mock_ensure_valid_city = mocker.patch(
        "app.services.job_ad_service.ensure_valid_city"
    )
    mock_perform_put_request = mocker.patch(
        "app.services.job_ad_service.perform_put_request",
        return_value=td.JOB_AD,
    )
    mock_job_ad_response = mocker.patch(
        "app.services.job_ad_service.JobAdResponse",
        return_value=job_ad_response,
    )

    # Act
    result = job_ad_service.update(job_ad_id, company_id, job_ad_data)

    # Assert
    mock_ensure_valid_job_ad_id.assert_called_once_with(
        job_ad_id=job_ad_id, company_id=company_id
    )
    if job_ad_data.location is not None:
        mock_ensure_valid_city.assert_called_once_with(name=job_ad_data.location)
    mock_perform_put_request.assert_called_once_with(
        url=f"{JOB_AD_BY_ID_URL.format(job_ad_id=job_ad_id)}",
        json=job_ad_data.model_dump(mode="json"),
    )
    mock_job_ad_response.assert_called_once_with(**td.JOB_AD)
    assert result == job_ad_response


def test_addSkillRequirement_addsSkill_whenDataIsValid(mocker) -> None:
    # Arrange
    job_ad_id = td.VALID_JOB_AD_ID
    skill_id = td.VALID_SKILL_ID
    message_response = mocker.Mock(spec=MessageResponse)

    mock_perform_post_request = mocker.patch(
        "app.services.job_ad_service.perform_post_request",
    )
    mock_message_response = mocker.patch(
        "app.services.job_ad_service.MessageResponse",
        return_value=message_response,
    )

    # Act
    result = job_ad_service.add_skill_requirement(job_ad_id, skill_id)

    # Assert
    mock_perform_post_request.assert_called_once_with(
        url=JOB_AD_ADD_SKILL_URL.format(job_ad_id=job_ad_id, skill_id=skill_id),
    )
    mock_message_response.assert_called_once_with(message="Skill added to job ad")
    assert result == message_response
