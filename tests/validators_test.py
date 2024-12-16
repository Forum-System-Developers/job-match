import pytest
from fastapi import status

from app.exceptions.custom_exceptions import ApplicationError
from app.services.external_db_service_urls import CITIES_URL, COMPANY_BY_ID_URL
from app.services.utils.validators import (
    ensure_no_match_request,
    ensure_valid_city,
    ensure_valid_company_id,
    ensure_valid_job_ad_id,
    ensure_valid_job_application_id,
    is_unique_email,
    is_unique_username,
)
from tests import test_data as td


def test_ensureValidCity_returnsCity_whenCityIsFound(mocker):
    # Arrange
    mock_perform_get_request = mocker.patch(
        "app.services.utils.validators.perform_get_request", return_value=td.CITY
    )

    # Act
    result = ensure_valid_city(name=td.VALID_CITY_NAME)

    # Assert
    mock_perform_get_request.assert_called_once_with(
        f"{CITIES_URL}/by-name/{td.VALID_CITY_NAME}"
    )
    assert result.name == td.VALID_CITY_NAME


def test_ensureValidJobAdId_returnsJobAd_whenJobAdIsFound(mocker):
    # Arrange
    mock_get_job_ad_by_id = mocker.patch(
        "app.services.utils.validators.get_job_ad_by_id",
        return_value=mocker.Mock(**td.JOB_AD),
    )

    # Act
    result = ensure_valid_job_ad_id(job_ad_id=td.VALID_JOB_AD_ID)

    # Assert
    mock_get_job_ad_by_id.assert_called_once_with(job_ad_id=td.VALID_JOB_AD_ID)
    assert result.id == td.VALID_JOB_AD_ID


def test_ensureValidJobAdId_raisesApplicationError_whenJobAdIsNotFound(mocker):
    # Arrange
    mock_get_job_ad_by_id = mocker.patch(
        "app.services.utils.validators.get_job_ad_by_id", return_value=None
    )

    # Act
    with pytest.raises(ApplicationError) as exc:
        ensure_valid_job_ad_id(job_ad_id=td.NON_EXISTENT_ID)

    # Assert
    mock_get_job_ad_by_id.assert_called_once_with(job_ad_id=td.NON_EXISTENT_ID)
    assert exc.value.data.status == status.HTTP_404_NOT_FOUND
    assert exc.value.data.detail == f"Job Ad with id {td.NON_EXISTENT_ID} not found"


def test_ensureValidJobAdId_raisesApplicationError_whenJobAdDoesNotBelongToCompany(
    mocker,
):
    # Arrange
    mock_get_job_ad_by_id = mocker.patch(
        "app.services.utils.validators.get_job_ad_by_id",
        return_value=mocker.Mock(**td.JOB_AD),
    )

    # Act
    with pytest.raises(ApplicationError) as exc:
        ensure_valid_job_ad_id(
            job_ad_id=td.VALID_JOB_AD_ID, company_id=td.NON_EXISTENT_ID
        )

    # Assert
    mock_get_job_ad_by_id.assert_called_once_with(job_ad_id=td.VALID_JOB_AD_ID)
    assert exc.value.data.status == status.HTTP_400_BAD_REQUEST
    assert (
        exc.value.data.detail
        == f"Job Ad with id {td.VALID_JOB_AD_ID} does not belong to company with id {td.NON_EXISTENT_ID}"
    )


def test_ensureValidJobAdId_returnsJobAd_whenCompanyIsProvided(mocker):
    # Arrange
    mock_get_job_ad_by_id = mocker.patch(
        "app.services.utils.validators.get_job_ad_by_id",
        return_value=mocker.Mock(**td.JOB_AD),
    )

    # Act
    result = ensure_valid_job_ad_id(
        job_ad_id=td.VALID_JOB_AD_ID, company_id=td.VALID_COMPANY_ID
    )

    # Assert
    mock_get_job_ad_by_id.assert_called_once_with(job_ad_id=td.VALID_JOB_AD_ID)
    assert result.id == td.VALID_JOB_AD_ID
    assert result.company_id == td.VALID_COMPANY_ID


def test_ensureValidJobApplicationId_returnsJobApplication_whenJobApplicationIsFound(
    mocker,
):
    # Arrange
    mock_get_job_application_by_id = mocker.patch(
        "app.services.utils.validators.get_job_application_by_id",
        return_value=mocker.Mock(**td.JOB_APPLICATION),
    )

    # Act
    result = ensure_valid_job_application_id(
        job_application_id=td.VALID_JOB_APPLICATION_ID
    )

    # Assert
    mock_get_job_application_by_id.assert_called_once_with(
        job_application_id=td.VALID_JOB_APPLICATION_ID
    )
    assert result.id == td.VALID_JOB_APPLICATION_ID


def test_ensureValidJobApplicationId_raisesApplicationError_whenJobApplicationIsNotFound(
    mocker,
):
    # Arrange
    mock_get_job_application_by_id = mocker.patch(
        "app.services.utils.validators.get_job_application_by_id", return_value=None
    )

    # Act
    with pytest.raises(ApplicationError) as exc:
        ensure_valid_job_application_id(job_application_id=td.NON_EXISTENT_ID)

    # Assert
    mock_get_job_application_by_id.assert_called_once_with(
        job_application_id=td.NON_EXISTENT_ID
    )
    assert exc.value.data.status == status.HTTP_404_NOT_FOUND
    assert (
        exc.value.data.detail
        == f"Job Application with id {td.NON_EXISTENT_ID} not found"
    )


def test_ensureValidJobApplicationId_raisesApplicationError_whenJobApplicationDoesNotBelongToProfessional(
    mocker,
):
    # Arrange
    mock_get_job_application_by_id = mocker.patch(
        "app.services.utils.validators.get_job_application_by_id",
        return_value=mocker.Mock(**td.JOB_APPLICATION),
    )

    # Act
    with pytest.raises(ApplicationError) as exc:
        ensure_valid_job_application_id(
            job_application_id=td.VALID_JOB_APPLICATION_ID,
            professional_id=td.NON_EXISTENT_ID,
        )

    # Assert
    mock_get_job_application_by_id.assert_called_once_with(
        job_application_id=td.VALID_JOB_APPLICATION_ID
    )
    assert exc.value.data.status == status.HTTP_400_BAD_REQUEST
    assert (
        exc.value.data.detail
        == f"Job Application with id {td.VALID_JOB_APPLICATION_ID} does not belong to professional with id {td.NON_EXISTENT_ID}"
    )


def test_ensureValidJobApplicationId_returnsJobApplication_whenProfessionalIsProvided(
    mocker,
):
    # Arrange
    mock_get_job_application_by_id = mocker.patch(
        "app.services.utils.validators.get_job_application_by_id",
        return_value=mocker.Mock(**td.JOB_APPLICATION),
    )

    # Act
    result = ensure_valid_job_application_id(
        job_application_id=td.VALID_JOB_APPLICATION_ID,
        professional_id=td.VALID_PROFESSIONAL_ID,
    )

    # Assert
    mock_get_job_application_by_id.assert_called_once_with(
        job_application_id=td.VALID_JOB_APPLICATION_ID
    )
    assert result.id == td.VALID_JOB_APPLICATION_ID
    assert result.professional_id == td.VALID_PROFESSIONAL_ID


def test_ensureValidCompanyId_returnsCompany_whenCompanyIsFound(mocker):
    # Arrange
    mock_perform_get_request = mocker.patch(
        "app.services.utils.validators.perform_get_request", return_value=td.COMPANY
    )

    # Act
    result = ensure_valid_company_id(company_id=td.VALID_COMPANY_ID)

    # Assert
    mock_perform_get_request.assert_called_once_with(
        url=f"{COMPANY_BY_ID_URL.format(company_id=td.VALID_COMPANY_ID)}"
    )
    assert result.id == td.VALID_COMPANY_ID


def test_ensureNoMatchRequest_doesNotRaiseError_whenNoMatchRequestExists(mocker):
    # Arrange
    mock_get_match_request_by_id = mocker.patch(
        "app.services.utils.validators.get_match_request_by_id", return_value=None
    )

    # Act & Assert
    ensure_no_match_request(
        job_ad_id=td.VALID_JOB_AD_ID, job_application_id=td.VALID_JOB_APPLICATION_ID
    )
    mock_get_match_request_by_id.assert_called_once_with(
        job_ad_id=td.VALID_JOB_AD_ID, job_application_id=td.VALID_JOB_APPLICATION_ID
    )


def test_ensureNoMatchRequest_raisesApplicationError_whenMatchRequestExists(mocker):
    # Arrange
    mock_get_match_request_by_id = mocker.patch(
        "app.services.utils.validators.get_match_request_by_id",
        return_value=mocker.Mock(),
    )

    # Act
    with pytest.raises(ApplicationError) as exc:
        ensure_no_match_request(
            job_ad_id=td.VALID_JOB_AD_ID, job_application_id=td.VALID_JOB_APPLICATION_ID
        )

    # Assert
    mock_get_match_request_by_id.assert_called_once_with(
        job_ad_id=td.VALID_JOB_AD_ID, job_application_id=td.VALID_JOB_APPLICATION_ID
    )
    assert exc.value.data.status == status.HTTP_400_BAD_REQUEST
    assert (
        exc.value.data.detail
        == f"Match request between job ad with id {td.VALID_JOB_AD_ID} and job application with id {td.VALID_JOB_APPLICATION_ID} already exists"
    )


def test_isUniqueUsername_returnsTrue_whenUsernameIsUnique(mocker):
    # Arrange
    unique_username = "unique_username"
    mock_get_professional_by_username = mocker.patch(
        "app.services.utils.validators.get_professional_by_username", return_value=None
    )
    mock_get_company_by_username = mocker.patch(
        "app.services.utils.validators.get_company_by_username", return_value=None
    )

    # Act
    result = is_unique_username(username=unique_username)

    # Assert
    mock_get_professional_by_username.assert_called_once_with(unique_username)
    mock_get_company_by_username.assert_called_once_with(unique_username)
    assert result is True


def test_isUniqueUsername_returnsFalse_whenUsernameBelongsToProfessional(mocker):
    # Arrange
    existing_username = "existing_username"
    mock_get_professional_by_username = mocker.patch(
        "app.services.utils.validators.get_professional_by_username",
        return_value=mocker.Mock(),
    )
    mock_get_company_by_username = mocker.patch(
        "app.services.utils.validators.get_company_by_username", return_value=None
    )

    # Act
    result = is_unique_username(username=existing_username)

    # Assert
    mock_get_professional_by_username.assert_called_once_with(existing_username)
    mock_get_company_by_username.assert_not_called()
    assert result is False


def test_isUniqueUsername_returnsFalse_whenUsernameBelongsToCompany(mocker):
    # Arrange
    existing_username = "existing_username"
    mock_get_professional_by_username = mocker.patch(
        "app.services.utils.validators.get_professional_by_username", return_value=None
    )
    mock_get_company_by_username = mocker.patch(
        "app.services.utils.validators.get_company_by_username",
        return_value=mocker.Mock(),
    )

    # Act
    result = is_unique_username(username=existing_username)

    # Assert
    mock_get_professional_by_username.assert_called_once_with(existing_username)
    mock_get_company_by_username.assert_called_once_with(existing_username)
    assert result is False


def test_isUniqueEmail_returnsTrue_whenEmailIsUnique(mocker):
    # Arrange
    unique_email = "unique_email@example.com"
    mock_get_professional_by_email = mocker.patch(
        "app.services.utils.validators.get_professional_by_email", return_value=None
    )
    mock_get_company_by_email = mocker.patch(
        "app.services.utils.validators.get_company_by_email", return_value=None
    )

    # Act
    result = is_unique_email(email=unique_email)

    # Assert
    mock_get_professional_by_email.assert_called_once_with(unique_email)
    mock_get_company_by_email.assert_called_once_with(unique_email)
    assert result is True


def test_isUniqueEmail_returnsFalse_whenEmailBelongsToProfessional(mocker):
    # Arrange
    existing_email = "existing_email@example.com"
    mock_get_professional_by_email = mocker.patch(
        "app.services.utils.validators.get_professional_by_email",
        return_value=mocker.Mock(),
    )
    mock_get_company_by_email = mocker.patch(
        "app.services.utils.validators.get_company_by_email", return_value=None
    )

    # Act
    result = is_unique_email(email=existing_email)

    # Assert
    mock_get_professional_by_email.assert_called_once_with(existing_email)
    mock_get_company_by_email.assert_not_called()
    assert result is False


def test_isUniqueEmail_returnsFalse_whenEmailBelongsToCompany(mocker):
    # Arrange
    existing_email = "existing_email@example.com"
    mock_get_professional_by_email = mocker.patch(
        "app.services.utils.validators.get_professional_by_email", return_value=None
    )
    mock_get_company_by_email = mocker.patch(
        "app.services.utils.validators.get_company_by_email", return_value=mocker.Mock()
    )

    # Act
    result = is_unique_email(email=existing_email)

    # Assert
    mock_get_professional_by_email.assert_called_once_with(existing_email)
    mock_get_company_by_email.assert_called_once_with(existing_email)
    assert result is False
