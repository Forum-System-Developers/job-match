import pytest
from fastapi import status

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.common import MessageResponse
from app.schemas.job_application import JobApplicationResponse, JobSearchStatus
from app.schemas.match import MatchRequestAd
from app.schemas.professional import ProfessionalResponse
from app.schemas.skill import SkillResponse
from app.services import professional_service
from app.services.external_db_service_urls import (
    PROFESSIONAL_BY_USERNAME_URL,
    PROFESSIONALS_BY_ID_URL,
    PROFESSIONALS_CV_URL,
    PROFESSIONALS_JOB_APPLICATIONS_URL,
    PROFESSIONALS_PHOTO_URL,
    PROFESSIONALS_SKILLS_URL,
    PROFESSIONALS_TOGGLE_STATUS_URL,
    PROFESSIONALS_URL,
)
from tests import test_data as td


def test_create_createsProfessional_whenDataIsValid(mocker) -> None:
    # Arrange
    professional_request = td.PROFESSIONAL_REQUEST
    professional_data = professional_request.professional
    city_mock = mocker.Mock(id=td.VALID_CITY_ID, name=professional_data.city)
    hashed_password = "hashed_password"
    professional_response = mocker.MagicMock()

    mock_validate_unique = mocker.patch(
        "app.services.professional_service._validate_unique_professional_details"
    )
    mock_city_service = mocker.patch(
        "app.services.city_service.get_by_name", return_value=city_mock
    )
    mock_hash_password = mocker.patch(
        "app.services.professional_service.hash_password", return_value=hashed_password
    )
    mock_perform_post_request = mocker.patch(
        "app.services.professional_service.perform_post_request",
        return_value=professional_response,
    )
    mock_send_mail = mocker.patch("app.services.professional_service.get_mail_service")
    mock_professional_response = mocker.patch(
        "app.services.professional_service.ProfessionalResponse",
        return_value=professional_response,
    )

    # Act
    response = professional_service.create(professional_request=professional_request)

    # Assert
    mock_validate_unique.assert_called_once_with(professional_create=professional_data)
    mock_city_service.assert_called_once_with(city_name=professional_data.city)
    mock_hash_password.assert_called_once_with(password=professional_data.password)
    mock_perform_post_request.assert_called_once()
    mock_send_mail.assert_called_once()
    assert response == professional_response


def test_getOrCreateFromGoogleToken_createsNewProfessional(mocker) -> None:
    # Arrange
    token_payload = mocker.MagicMock()
    city_mock = mocker.Mock(id=td.VALID_CITY_ID, name="Default City")
    mock_professional_request = mocker.Mock()
    mock_professional_body_request = mocker.Mock()
    mock_professional_response = mocker.Mock()

    mock_get_professional_by_sub = mocker.patch(
        "app.services.professional_service.get_professional_by_sub",
        return_value=None,
    )
    mock_get_default_city = mocker.patch(
        "app.services.city_service.get_default", return_value=city_mock
    )
    mock_generate_temporary_credentials = mocker.patch(
        "app.services.professional_service._generate_temporary_credentials",
        return_value=("temp_username", "temp_password"),
    )
    mock_create_professional = mocker.patch(
        "app.services.professional_service.create",
        return_value=mock_professional_response,
    )
    mock_professional_create = mocker.patch(
        "app.services.professional_service.ProfessionalCreate",
        return_value=mock_professional_request,
    )
    mock_professional_request_body = mocker.patch(
        "app.services.professional_service.ProfessionalRequestBody",
        return_value=mock_professional_body_request,
    )
    mock_create_professional = mocker.patch(
        "app.services.professional_service.create",
        return_value=mock_professional_response,
    )

    # Act
    response = professional_service.get_or_create_from_google_token(
        token_payload=token_payload
    )

    # Assert
    mock_get_professional_by_sub.assert_called_once_with(sub=token_payload["sub"])
    mock_get_default_city.assert_called_once()
    mock_generate_temporary_credentials.assert_called_once()
    mock_create_professional.assert_called_once()
    assert response == mock_professional_response


def test_getOrCreateFromGoogleToken_returnsExistingProfessional(mocker) -> None:
    # Arrange
    token_payload = mocker.MagicMock()
    professional = mocker.MagicMock()

    mock_get_professional_by_sub = mocker.patch(
        "app.services.professional_service.get_professional_by_sub",
        return_value=professional,
    )

    # Act
    response = professional_service.get_or_create_from_google_token(
        token_payload=token_payload
    )

    # Assert
    mock_get_professional_by_sub.assert_called_once_with(sub=token_payload["sub"])
    assert response == professional


def test_update_updatesProfessional_whenDataIsValid(mocker) -> None:
    # Arrange
    professional_id = td.VALID_PROFESSIONAL_ID
    professional_request = mocker.MagicMock()
    professional_data = professional_request.professional
    city_mock = mocker.Mock(id=td.VALID_CITY_ID, name=professional_data.city)
    professional_response = mocker.MagicMock()

    mock_city_service = mocker.patch(
        "app.services.city_service.get_by_name", return_value=city_mock
    )
    mock_perform_put_request = mocker.patch(
        "app.services.professional_service.perform_put_request",
        return_value=professional_response,
    )
    mock_professional_response = mocker.patch(
        "app.services.professional_service.ProfessionalResponse",
        return_value=professional_response,
    )
    mock_professional_update_final = mocker.patch(
        "app.services.professional_service.ProfessionalUpdateFinal",
        return_value=professional_request,
    )

    # Act
    response = professional_service.update(
        professional_id=professional_id, professional_request=professional_request
    )

    # Assert
    mock_city_service.assert_called_once_with(city_name=professional_data.city)
    mock_perform_put_request.assert_called_once()
    assert response == professional_response


def test_update_updatesProfessional_whenCityIsNone(mocker) -> None:
    # Arrange
    professional_id = td.VALID_PROFESSIONAL_ID
    professional_request = mocker.MagicMock()
    professional_response = mocker.MagicMock()
    professional_request.professional.city = None

    mock_perform_put_request = mocker.patch(
        "app.services.professional_service.perform_put_request",
        return_value=professional_response,
    )
    mock_professional_response = mocker.patch(
        "app.services.professional_service.ProfessionalResponse",
        return_value=professional_response,
    )
    mock_professional_update_final = mocker.patch(
        "app.services.professional_service.ProfessionalUpdateFinal",
        return_value=professional_request,
    )

    # Act
    response = professional_service.update(
        professional_id=professional_id, professional_request=professional_request
    )

    # Assert
    mock_perform_put_request.assert_called_once()
    assert response == professional_response


def test_upload_photo_uploadsPhotoSuccessfully(mocker) -> None:
    # Arrange
    professional_id = td.VALID_PROFESSIONAL_ID
    photo = mocker.Mock()
    photo.filename = "photo.png"
    photo.file = mocker.Mock()
    photo.content_type = "image/png"
    message_response = MessageResponse(message="Photo uploaded successfully")

    mock_validate_uploaded_file = mocker.patch(
        "app.services.professional_service.validate_uploaded_file"
    )
    mock_perform_post_request = mocker.patch(
        "app.services.professional_service.perform_post_request"
    )

    # Act
    response = professional_service.upload_photo(
        professional_id=professional_id, photo=photo
    )

    # Assert
    mock_validate_uploaded_file.assert_called_once_with(photo)
    mock_perform_post_request.assert_called_once_with(
        url=f"{PROFESSIONALS_PHOTO_URL.format(professional_id=professional_id)}",
        files={"photo": (photo.filename, photo.file, photo.content_type)},
    )
    assert response == message_response


def test_upload_cv_uploadsCVSuccessfully(mocker) -> None:
    # Arrange
    professional_id = td.VALID_PROFESSIONAL_ID
    cv = mocker.Mock()
    cv.filename = "test.pdf"
    cv.file = mocker.Mock()
    cv.content_type = "application/pdf"
    message_response = MessageResponse(message="CV uploaded successfully")

    mock_validate_uploaded_cv = mocker.patch(
        "app.services.professional_service.validate_uploaded_cv"
    )
    mock_perform_post_request = mocker.patch(
        "app.services.professional_service.perform_post_request"
    )

    # Act
    response = professional_service.upload_cv(professional_id=professional_id, cv=cv)

    # Assert
    mock_validate_uploaded_cv.assert_called_once_with(cv)
    mock_perform_post_request.assert_called_once_with(
        url=f"{PROFESSIONALS_CV_URL.format(professional_id=professional_id)}",
        files={"cv": (cv.filename, cv.file, cv.content_type)},
    )
    assert response == message_response


def test_downloadPhoto_downloadsPhotoSuccessfully(mocker) -> None:
    # Arrange
    professional_id = td.VALID_PROFESSIONAL_ID
    photo_content = b"photo_content"
    mock_response = mocker.Mock()
    mock_response.content = photo_content

    mock_perform_get_request = mocker.patch(
        "app.services.professional_service.perform_get_request",
        return_value=mock_response,
    )
    mock_streaming_response = mocker.patch(
        "app.services.professional_service.StreamingResponse",
        return_value=mock_response,
    )

    # Act
    response = professional_service.download_photo(professional_id=professional_id)

    # Assert
    mock_perform_get_request.assert_called_once_with(
        url=f"{PROFESSIONALS_PHOTO_URL.format(professional_id=professional_id)}"
    )
    assert response == mock_response


def test_download_cv_downloadsCVSuccessfully(mocker) -> None:
    # Arrange
    professional_id = td.VALID_PROFESSIONAL_ID
    cv_content = b"cv_content"
    mock_response = mocker.Mock()
    mock_response.content = cv_content
    mock_response.headers = {"Content-Disposition": "attachment; filename=test.pdf"}
    mock_streaming_response = mocker.Mock()

    mock_perform_get_request = mocker.patch(
        "app.services.professional_service.perform_get_request",
        return_value=mock_response,
    )
    mock_create_cv_streaming_response = mocker.patch(
        "app.services.professional_service._create_cv_streaming_response",
        return_value=mock_streaming_response,
    )

    # Act
    response = professional_service.download_cv(professional_id=professional_id)

    # Assert
    mock_perform_get_request.assert_called_once_with(
        url=f"{PROFESSIONALS_CV_URL.format(professional_id=professional_id)}"
    )
    mock_create_cv_streaming_response.assert_called_once_with(mock_response)
    assert response == mock_streaming_response


def test_delete_cv_deletesCVSuccessfully(mocker) -> None:
    # Arrange
    professional_id = td.VALID_PROFESSIONAL_ID
    message_response = MessageResponse(message="CV deleted successfully")

    mock_perform_delete_request = mocker.patch(
        "app.services.professional_service.perform_delete_request"
    )

    # Act
    response = professional_service.delete_cv(professional_id=professional_id)

    # Assert
    mock_perform_delete_request.assert_called_once_with(
        url=f"{PROFESSIONALS_CV_URL.format(professional_id=professional_id)}"
    )
    assert response == message_response


def test_get_by_id_returnsProfessional_whenIdIsValid(mocker) -> None:
    # Arrange
    professional_id = td.VALID_PROFESSIONAL_ID
    professional_response = mocker.MagicMock()

    mock_perform_get_request = mocker.patch(
        "app.services.professional_service.perform_get_request",
        return_value=professional_response,
    )
    mock_professional_response = mocker.patch(
        "app.services.professional_service.ProfessionalResponse",
        return_value=professional_response,
    )

    # Act
    response = professional_service.get_by_id(professional_id=professional_id)

    # Assert
    mock_perform_get_request.assert_called_once_with(
        url=f"{PROFESSIONALS_BY_ID_URL.format(professional_id=professional_id)}"
    )
    assert response == professional_response


def test_getAll_returnsProfessionals_whenDataIsValid(mocker) -> None:
    # Arrange
    filter_params = mocker.MagicMock()
    search_params = mocker.MagicMock()
    professionals_response = [mocker.MagicMock(), mocker.MagicMock()]

    mock_perform_get_request = mocker.patch(
        "app.services.professional_service.perform_get_request",
        return_value=professionals_response,
    )
    mock_professional_response = mocker.patch(
        "app.services.professional_service.ProfessionalResponse",
        side_effect=professionals_response,
    )

    # Act
    response = professional_service.get_all(
        filter_params=filter_params, search_params=search_params
    )

    # Assert
    mock_perform_get_request.assert_called_once_with(
        url=PROFESSIONALS_URL,
        params={
            **search_params.model_dump(mode="json"),
            **filter_params.model_dump(mode="json"),
        },
    )
    assert response == professionals_response


def test_getAll_returnsEmptyList_whenNoProfessionalsFound(mocker) -> None:
    # Arrange
    filter_params = mocker.MagicMock()
    search_params = mocker.MagicMock()
    professionals_response: list[ProfessionalResponse] = []

    mock_perform_get_request = mocker.patch(
        "app.services.professional_service.perform_get_request",
        return_value=professionals_response,
    )

    # Act
    response = professional_service.get_all(
        filter_params=filter_params, search_params=search_params
    )

    # Assert
    mock_perform_get_request.assert_called_once_with(
        url=PROFESSIONALS_URL,
        params={
            **search_params.model_dump(mode="json"),
            **filter_params.model_dump(mode="json"),
        },
    )
    assert response == professionals_response


def test_getById_returnsProfessional_whenIdIsValid(mocker) -> None:
    # Arrange
    professional_id = td.VALID_PROFESSIONAL_ID
    professional_response = mocker.MagicMock()

    mock_get_professional_by_id = mocker.patch(
        "app.services.professional_service.get_professional_by_id",
        return_value=professional_response,
    )

    # Act
    response = professional_service._get_by_id(professional_id=professional_id)

    # Assert
    mock_get_professional_by_id.assert_called_once_with(professional_id=professional_id)
    assert response == professional_response


def test_getById_raisesApplicationError_whenProfessionalNotFound(mocker) -> None:
    # Arrange
    professional_id = td.NON_EXISTENT_ID

    mock_get_professional_by_id = mocker.patch(
        "app.services.professional_service.get_professional_by_id",
        return_value=None,
    )

    # Act & Assert
    with pytest.raises(ApplicationError) as exc_info:
        professional_service._get_by_id(professional_id=professional_id)

    mock_get_professional_by_id.assert_called_once_with(professional_id=professional_id)
    assert exc_info.value.data.status == status.HTTP_404_NOT_FOUND
    assert (
        exc_info.value.data.detail
        == f"Professional with id {professional_id} not found"
    )


def test_setMatchesStatus_setsPrivateStatusSuccessfully(mocker) -> None:
    # Arrange
    professional_id = td.VALID_PROFESSIONAL_ID
    private_matches = mocker.MagicMock(status=True)
    message_response = MessageResponse(message="Matches set as private")

    mock_perform_patch_request = mocker.patch(
        "app.services.professional_service.perform_patch_request"
    )

    # Act
    response = professional_service.set_matches_status(
        professional_id=professional_id, private_matches=private_matches
    )

    # Assert
    mock_perform_patch_request.assert_called_once_with(
        url=f"{PROFESSIONALS_TOGGLE_STATUS_URL.format(professional_id=professional_id)}",
        json={**private_matches.model_dump(mode="json")},
    )
    assert response == message_response


def test_getByUsername_returnsUser_whenUsernameIsValid(mocker) -> None:
    # Arrange
    username = "valid_username"
    user_response = mocker.MagicMock()

    mock_perform_get_request = mocker.patch(
        "app.services.professional_service.perform_get_request",
        return_value=user_response,
    )
    mock_user_response = mocker.patch(
        "app.services.professional_service.User",
        return_value=user_response,
    )

    # Act
    response = professional_service.get_by_username(username=username)

    # Assert
    mock_perform_get_request.assert_called_once_with(
        url=f"{PROFESSIONAL_BY_USERNAME_URL.format(username=username)}"
    )
    assert response == user_response


def test_getApplications_returnsApplications_whenDataIsValid(mocker) -> None:
    # Arrange
    professional_id = td.VALID_PROFESSIONAL_ID
    application_status = JobSearchStatus.ACTIVE
    filter_params = mocker.MagicMock()
    job_applications_response = [mocker.MagicMock(), mocker.MagicMock()]

    mock_perform_get_request = mocker.patch(
        "app.services.professional_service.perform_get_request",
        return_value=job_applications_response,
    )
    mock_job_application_response = mocker.patch(
        "app.services.professional_service.JobApplicationResponse",
        side_effect=job_applications_response,
    )

    # Act
    response = professional_service.get_applications(
        professional_id=professional_id,
        application_status=application_status,
        filter_params=filter_params,
    )

    # Assert
    mock_perform_get_request.assert_called_once_with(
        url=PROFESSIONALS_JOB_APPLICATIONS_URL.format(professional_id=professional_id),
        params={
            **filter_params.model_dump(mode="json"),
            "application_status": application_status.value,
        },
    )
    assert response == job_applications_response


def test_getApplications_returnsEmptyList_whenNoApplicationsFound(mocker) -> None:
    # Arrange
    professional_id = td.VALID_PROFESSIONAL_ID
    application_status = JobSearchStatus.ACTIVE
    filter_params = mocker.MagicMock()
    job_applications_response: list[JobApplicationResponse] = []

    mock_perform_get_request = mocker.patch(
        "app.services.professional_service.perform_get_request",
        return_value=job_applications_response,
    )

    # Act
    response = professional_service.get_applications(
        professional_id=professional_id,
        application_status=application_status,
        filter_params=filter_params,
    )

    # Assert
    mock_perform_get_request.assert_called_once_with(
        url=PROFESSIONALS_JOB_APPLICATIONS_URL.format(professional_id=professional_id),
        params={
            **filter_params.model_dump(mode="json"),
            "application_status": application_status.value,
        },
    )
    assert response == job_applications_response


def test_getSkills_returnsSkills_whenDataIsValid(mocker) -> None:
    # Arrange
    professional_id = td.VALID_PROFESSIONAL_ID
    skills_response = [mocker.MagicMock(), mocker.MagicMock()]

    mock_perform_get_request = mocker.patch(
        "app.services.professional_service.perform_get_request",
        return_value=skills_response,
    )
    mock_skill_response = mocker.patch(
        "app.services.professional_service.SkillResponse",
        side_effect=skills_response,
    )

    # Act
    response = professional_service.get_skills(professional_id=professional_id)

    # Assert
    mock_perform_get_request.assert_called_once_with(
        url=f"{PROFESSIONALS_SKILLS_URL.format(professional_id=professional_id)}"
    )
    assert response == skills_response


def test_getSkills_returnsEmptyList_whenNoSkillsFound(mocker) -> None:
    # Arrange
    professional_id = td.VALID_PROFESSIONAL_ID
    skills_response: list[SkillResponse] = []

    mock_perform_get_request = mocker.patch(
        "app.services.professional_service.perform_get_request",
        return_value=skills_response,
    )

    # Act
    response = professional_service.get_skills(professional_id=professional_id)

    # Assert
    mock_perform_get_request.assert_called_once_with(
        url=f"{PROFESSIONALS_SKILLS_URL.format(professional_id=professional_id)}"
    )
    assert response == skills_response


def test_getMatchRequests_returnsMatchRequests_whenDataIsValid(mocker) -> None:
    # Arrange
    professional_id = td.VALID_PROFESSIONAL_ID
    match_requests_response = [mocker.MagicMock(), mocker.MagicMock()]

    mock_get_by_id = mocker.patch(
        "app.services.professional_service._get_by_id",
        return_value=mocker.MagicMock(id=professional_id),
    )
    mock_get_match_requests_for_professional = mocker.patch(
        "app.services.match_service.get_match_requests_for_professional",
        return_value=match_requests_response,
    )

    # Act
    response = professional_service.get_match_requests(professional_id=professional_id)

    # Assert
    mock_get_by_id.assert_called_once_with(professional_id=professional_id)
    mock_get_match_requests_for_professional.assert_called_once_with(
        professional_id=professional_id
    )
    assert response == match_requests_response


def test_getMatchRequests_returnsEmptyList_whenNoMatchRequestsFound(mocker) -> None:
    # Arrange
    professional_id = td.VALID_PROFESSIONAL_ID
    match_requests_response: list[MatchRequestAd] = []

    mock_get_by_id = mocker.patch(
        "app.services.professional_service._get_by_id",
        return_value=mocker.MagicMock(id=professional_id),
    )
    mock_get_match_requests_for_professional = mocker.patch(
        "app.services.match_service.get_match_requests_for_professional",
        return_value=match_requests_response,
    )

    # Act
    response = professional_service.get_match_requests(professional_id=professional_id)

    # Assert
    mock_get_by_id.assert_called_once_with(professional_id=professional_id)
    mock_get_match_requests_for_professional.assert_called_once_with(
        professional_id=professional_id
    )
    assert response == match_requests_response


def test_createCvStreamingResponse_createsStreamingResponseSuccessfully(mocker) -> None:
    # Arrange
    response_headers = {"Content-Disposition": "attachment; filename=test.pdf"}
    mock_response = mocker.Mock()
    mock_response.content = b"cv_content"
    mock_response.media_type = "application/pdf"
    mock_response.headers = response_headers

    mock_streaming_response = mocker.patch(
        "app.services.professional_service.StreamingResponse",
        return_value=mock_response,
    )

    # Act
    result = professional_service._create_cv_streaming_response(response=mock_response)

    # Assert
    assert result == mock_response
    assert result.media_type == "application/pdf"
    assert (
        result.headers["Content-Disposition"] == response_headers["Content-Disposition"]
    )
    assert result.headers["Access-Control-Expose-Headers"] == "Content-Disposition"


def test_validateUniqueProfessionalDetails_raisesError_whenUsernameIsNotUnique(
    mocker,
) -> None:
    # Arrange
    professional_create = mocker.Mock(
        username="existing_username", email="existing_email@example.com"
    )

    mock_is_unique_username = mocker.patch(
        "app.services.professional_service.is_unique_username",
        return_value=False,
    )
    mock_is_unique_email = mocker.patch(
        "app.services.professional_service.is_unique_email",
        return_value=True,
    )

    # Act & Assert
    with pytest.raises(ApplicationError) as exc_info:
        professional_service._validate_unique_professional_details(
            professional_create=professional_create
        )

    mock_is_unique_username.assert_called_once_with(
        username=professional_create.username
    )
    mock_is_unique_email.assert_not_called()
    assert exc_info.value.data.status == status.HTTP_409_CONFLICT
    assert exc_info.value.data.detail == "Username already taken"


def test_validateUniqueProfessionalDetails_raisesError_whenEmailIsNotUnique(
    mocker,
) -> None:
    # Arrange
    professional_create = mocker.Mock(
        username="unique_username", email="existing_email@example.com"
    )

    mock_is_unique_username = mocker.patch(
        "app.services.professional_service.is_unique_username",
        return_value=True,
    )
    mock_is_unique_email = mocker.patch(
        "app.services.professional_service.is_unique_email",
        return_value=False,
    )

    # Act & Assert
    with pytest.raises(ApplicationError) as exc_info:
        professional_service._validate_unique_professional_details(
            professional_create=professional_create
        )

    mock_is_unique_username.assert_called_once_with(
        username=professional_create.username
    )
    mock_is_unique_email.assert_called_once_with(email=professional_create.email)
    assert exc_info.value.data.status == status.HTTP_409_CONFLICT
    assert exc_info.value.data.detail == "Email already taken"


def test_validateUniqueProfessionalDetails_passes_whenUsernameAndEmailAreUnique(
    mocker,
) -> None:
    # Arrange
    professional_create = mocker.Mock(
        username="unique_username", email="unique_email@example.com"
    )

    mock_is_unique_username = mocker.patch(
        "app.services.professional_service.is_unique_username",
        return_value=True,
    )
    mock_is_unique_email = mocker.patch(
        "app.services.professional_service.is_unique_email",
        return_value=True,
    )

    # Act
    professional_service._validate_unique_professional_details(
        professional_create=professional_create
    )

    # Assert
    mock_is_unique_username.assert_called_once_with(
        username=professional_create.username
    )
    mock_is_unique_email.assert_called_once_with(email=professional_create.email)


def test_generateTemporaryCredentials_generatesUniqueUsernameAndPassword(
    mocker,
) -> None:
    # Arrange
    mock_token_urlsafe = mocker.patch(
        "app.services.professional_service.secrets.token_urlsafe",
        return_value="unique_username",
    )
    mock_generate_patterned_password = mocker.patch(
        "app.services.professional_service.generate_patterned_password",
        return_value="unique_password",
    )

    # Act
    username, password = professional_service._generate_temporary_credentials()

    # Assert
    mock_token_urlsafe.assert_called_once_with(16)
    mock_generate_patterned_password.assert_called_once()
    assert username == "unique_username"
    assert password == "unique_password"
