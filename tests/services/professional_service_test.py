import json

import pytest
from fastapi import status
from fastapi.responses import JSONResponse, StreamingResponse

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.city import City
from app.schemas.common import MessageResponse
from app.schemas.job_ad import JobAdPreview
from app.schemas.job_application import JobSearchStatus
from app.schemas.user import User
from app.services import professional_service
from app.sql_app.job_application.job_application import JobApplication
from app.sql_app.professional.professional import Professional
from tests import test_data as td
from tests.utils import assert_filter_called_with


@pytest.fixture
def mock_db(mocker):
    return mocker.Mock()


def test_create_raises_error_when_city_not_found(mocker, mock_db) -> None:
    # Arrange
    professional_request = td.PROFESSIONAL_REQUEST
    mock_city_service = mocker.patch(
        "app.services.city_service.get_by_name", return_value=None
    )

    # Act & Assert
    with pytest.raises(ApplicationError) as exc:
        professional_service.create(
            professional_request=professional_request, db=mock_db
        )

    assert exc.value.data.detail == f"City with name {td.VALID_CITY_NAME} was not found"
    assert exc.value.data.status == status.HTTP_404_NOT_FOUND
    mock_city_service.assert_called_once_with(city_name=td.VALID_CITY_NAME, db=mock_db)


def test_create_creates_professional_when_city_found(mocker, mock_db) -> None:
    # Arrange
    city_mock = mocker.Mock(id=1, name="Sofia")
    professional_request = td.PROFESSIONAL_REQUEST
    professional_mock = mocker.Mock(**td.PROFESSIONAL_RESPONSE)
    response_mock = mocker.Mock(**td.PROFESSIONAL_RESPONSE)

    mock_city_service = mocker.patch(
        "app.services.city_service.get_by_name", return_value=city_mock
    )
    mock_register_professional = mocker.patch(
        "app.services.professional_service._register_professional",
        return_value=professional_mock,
    )
    mock_response_create = mocker.patch(
        "app.schemas.professional.ProfessionalResponse.create",
        return_value=response_mock,
    )

    # Act
    response = professional_service.create(
        professional_request=professional_request, db=mock_db
    )

    # Assert
    mock_city_service.assert_called_once_with(city_name=td.VALID_CITY_NAME, db=mock_db)
    mock_register_professional.assert_called_once_with(
        professional_create=professional_request.professional,
        professional_status=professional_request.status,
        city_id=city_mock.id,
        db=mock_db,
    )
    mock_response_create.assert_called_once_with(professional=professional_mock)

    assert response.id == professional_mock.id
    assert response.first_name == td.VALID_PROFESSIONAL_FIRST_NAME
    assert response.last_name == td.VALID_PROFESSIONAL_LAST_NAME
    assert response.email == td.VALID_PROFESSIONAL_EMAIL
    assert response.city == td.VALID_CITY_NAME


def test_update_update_professional_whenDataIsValid(mocker, mock_db):
    # Arrange
    mock_professional_data = mocker.Mock()
    mock_professional = mocker.Mock(id=td.VALID_PROFESSIONAL_ID)
    mock_response = mocker.Mock()

    mock_get_by_id = mocker.patch(
        "app.services.professional_service._get_by_id",
        return_value=mock_professional,
    )
    mock_update_attributes = mocker.patch(
        "app.services.professional_service._update_attributes",
        return_value=mock_professional,
    )
    mock_create = mocker.patch(
        "app.schemas.professional.ProfessionalResponse.create",
        return_value=mock_response,
    )

    # Act
    result = professional_service.update(
        professional_id=mock_professional.id,
        professional_request=mock_professional_data,
        db=mock_db,
    )

    # Assert
    mock_get_by_id.assert_called_once_with(
        professional_id=mock_professional.id, db=mock_db
    )
    mock_update_attributes.assert_called_once_with(
        professional=mock_professional,
        professional_request=mock_professional_data,
        db=mock_db,
    )
    mock_create.assert_called_once_with(
        professional=mock_professional, matched_ads=None
    )
    assert result == mock_response


def test_uploadPhoto_uploadsPhoto_whenFileIsValid(mocker, mock_db):
    # Arrange
    mock_professional = mocker.Mock(photo=None)
    professional_id = td.VALID_PROFESSIONAL_ID

    mock_get_by_id = mocker.patch(
        "app.services.professional_service._get_by_id",
        return_value=mock_professional,
    )

    mock_process_db_transaction = mocker.patch(
        "app.services.professional_service.process_db_transaction",
        side_effect=lambda transaction_func, db: transaction_func(),
    )

    mock_file_content = b"valid_file_content"
    mock_upload_file = mocker.Mock()
    mock_upload_file.file.read.return_value = mock_file_content
    mock_upload_file.file.seek.return_value = None

    # Act
    result = professional_service.upload_photo(
        professional_id=professional_id, photo=mock_upload_file, db=mock_db
    )

    # Assert
    mock_get_by_id.assert_called_once_with(professional_id=professional_id, db=mock_db)
    mock_upload_file.file.read.assert_called_once()
    mock_upload_file.file.seek.assert_called_once_with(0)
    mock_process_db_transaction.assert_called_once()
    assert mock_professional.photo == mock_file_content
    assert result == {"msg": "Photo successfully uploaded"}


def test_uploadPhoto_raisesApplicationError_whenFileExceedsSizeLimit(mocker, mock_db):
    # Arrange
    mock_professional = mocker.Mock()
    professional_id = td.VALID_PROFESSIONAL_ID

    mocker.patch(
        "app.services.professional_service._get_by_id",
        return_value=mock_professional,
    )
    mocker.patch(
        "app.services.professional_service.process_db_transaction",
        side_effect=lambda transaction_func, db: transaction_func(),
    )

    oversized_content = b"a" * (5 * 1024 * 1024 + 1)
    mock_upload_file = mocker.Mock()
    mock_upload_file.file.read.return_value = oversized_content
    mock_upload_file.file.seek.return_value = None

    # Act & Assert
    with pytest.raises(ApplicationError) as exc:
        professional_service.upload_photo(
            professional_id=professional_id, photo=mock_upload_file, db=mock_db
        )

    assert exc.value.data.detail == "File size exceeds the allowed limit of 5.0MB."
    assert exc.value.data.status == status.HTTP_400_BAD_REQUEST


def test_downloadPhoto_returnsPhoto_whenPhotoExists(mocker, mock_db):
    # Arrange
    professional_id = td.VALID_PROFESSIONAL_ID
    mock_professional = mocker.Mock()
    photo_data = b"somebinarydata"
    mock_professional.photo = photo_data

    mock_get_by_id = mocker.patch(
        "app.services.professional_service._get_by_id",
        return_value=mock_professional,
    )

    # Act
    response = professional_service.download_photo(
        professional_id=professional_id, db=mock_db
    )

    # Assert
    assert response.status_code == 200
    assert response.media_type == "image/png"
    mock_get_by_id.assert_called_once_with(professional_id=professional_id, db=mock_db)


def test_downloadPhoto_returnsMessage_whenPhotoIsNone(mocker, mock_db):
    # Arrange
    professional_id = td.VALID_PROFESSIONAL_ID
    mock_professional = mocker.Mock()
    mock_professional.photo = None

    mock_get_by_id = mocker.patch(
        "app.services.professional_service._get_by_id",
        return_value=mock_professional,
    )

    # Act
    response = professional_service.download_photo(
        professional_id=professional_id, db=mock_db
    )

    # Assert
    assert response.status_code == 200
    assert json.loads(response.body) == {"msg": "No available photo"}
    mock_get_by_id.assert_called_once_with(professional_id=professional_id, db=mock_db)


def test_get_by_id_whenProfessionalHasMatches(mocker, mock_db):
    # Arrange
    professional_id = td.VALID_PROFESSIONAL_ID
    mock_professional = mocker.Mock(**td.PROFESSIONAL_RESPONSE)

    mock_get_by_id = mocker.patch(
        "app.services.professional_service._get_by_id", return_value=mock_professional
    )
    mock_get_matches = mocker.patch(
        "app.services.professional_service._get_matches", return_value=["ad1", "ad2"]
    )
    mock_professional_response = mocker.patch(
        "app.services.professional_service.ProfessionalResponse.create",
        return_value="professional_response",
    )

    # Act
    response = professional_service.get_by_id(
        professional_id=professional_id, db=mock_db
    )

    # Assert
    mock_professional_response.assert_called_once_with(
        professional=mock_professional, matched_ads=["ad1", "ad2"]
    )
    assert response == "professional_response"
    mock_get_by_id.assert_called_once_with(professional_id=professional_id, db=mock_db)
    mock_get_matches.assert_called_once_with(
        professional_id=professional_id, db=mock_db
    )


def test_get_all_whenProfessionalsExist_withOrderByAsc(mocker, mock_db):
    # Arrange
    mock_filter_params = mocker.Mock(offset=0, limit=10)
    mock_search_params = mocker.Mock(skills=[], order="asc", order_by="created_at")
    mock_professionals = [mocker.Mock(), mocker.Mock()]
    mock_professional_response = [mocker.Mock(), mocker.Mock()]

    mock_query = mock_db.query.return_value
    mock_options = mock_query.options.return_value
    mock_filtered = mock_options.filter.return_value
    mock_offset = mock_filtered.offset.return_value
    mock_limit = mock_offset.limit.return_value
    mock_limit.all.return_value = mock_professionals

    mocker.patch(
        "app.schemas.professional.ProfessionalResponse.create",
        side_effect=mock_professional_response,
    )

    # Act
    response = professional_service.get_all(
        filter_params=mock_filter_params,
        search_params=mock_search_params,
        db=mock_db,
    )

    # Assert
    mock_db.query.assert_called_once_with(Professional)
    mock_query.options.assert_called_once()
    mock_options.filter.assert_called_once()
    mock_filtered.offset.assert_called_once_with(mock_filter_params.offset)
    mock_offset.limit.assert_called_once_with(mock_filter_params.limit)
    mock_limit.all.assert_called_once()
    assert len(response) == 2
    assert response[0] == mock_professional_response[0]
    assert response[1] == mock_professional_response[1]


def test_get_all_whenProfessionalsExist_withOrderByDesc(mocker, mock_db):
    # Arrange
    mock_filter_params = mocker.Mock(offset=0, limit=10)
    mock_search_params = mocker.Mock(skills=[], order="desc", order_by="created_at")
    mock_professionals = [mocker.Mock(), mocker.Mock()]
    mock_professional_response = [mocker.Mock(), mocker.Mock()]

    mock_query = mock_db.query.return_value
    mock_options = mock_query.options.return_value
    mock_filtered = mock_options.filter.return_value
    mock_offset = mock_filtered.offset.return_value
    mock_limit = mock_offset.limit.return_value
    mock_limit.all.return_value = mock_professionals

    mocker.patch(
        "app.schemas.professional.ProfessionalResponse.create",
        side_effect=mock_professional_response,
    )

    # Act
    response = professional_service.get_all(
        filter_params=mock_filter_params,
        search_params=mock_search_params,
        db=mock_db,
    )

    # Assert
    mock_db.query.assert_called_once_with(Professional)
    mock_query.options.assert_called_once()
    mock_options.filter.assert_called_once()
    mock_filtered.offset.assert_called_once_with(mock_filter_params.offset)
    mock_offset.limit.assert_called_once_with(mock_filter_params.limit)
    mock_limit.all.assert_called_once()
    assert len(response) == 2
    assert response[0] == mock_professional_response[0]
    assert response[1] == mock_professional_response[1]


def test_getAll_returnsProfessionalsFilteredBySkills_whenSkillsProvided(
    mocker, mock_db
):
    # Arrange
    mock_filter_params = mocker.Mock(offset=0, limit=10)
    mock_search_params = mocker.Mock(
        skills=["Python", "Django"], order="asc", order_by="first_name"
    )
    mock_professionals = [mocker.Mock(), mocker.Mock()]
    mock_professional_response = [mocker.Mock(), mocker.Mock()]

    mock_query = mock_db.query.return_value
    mock_options = mock_query.options.return_value
    mock_filtered_by_status = mock_options.filter.return_value
    # mock_filtered_by_skills = mock_filtered_by_status.filter.return_value
    mock_offset = mock_filtered_by_status.offset.return_value
    mock_limit = mock_offset.limit.return_value
    mock_limit.all.return_value = mock_professionals

    mocker.patch(
        "app.schemas.professional.ProfessionalResponse.create",
        side_effect=mock_professional_response,
    )

    # Act
    response = professional_service.get_all(
        filter_params=mock_filter_params,
        search_params=mock_search_params,
        db=mock_db,
    )

    # Assert
    assert len(response) == 2
    assert response[0] == mock_professional_response[0]
    assert response[1] == mock_professional_response[1]


def test_get_by_id_whenDataIsValid(mocker, mock_db):
    # Arrange
    professional = mocker.Mock(**td.PROFESSIONAL_MODEL)

    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = professional

    expected_professional = Professional(**td.PROFESSIONAL_MODEL)

    # Act
    response = professional_service._get_by_id(
        professional_id=td.VALID_PROFESSIONAL_ID, db=mock_db
    )

    # Assert
    assert response.id == expected_professional.id
    assert response.city_id == expected_professional.city_id
    assert response.username == expected_professional.username
    assert response.password == expected_professional.password
    assert response.description == expected_professional.description
    assert response.email == expected_professional.email
    assert response.photo == expected_professional.photo
    assert response.status == expected_professional.status
    assert (
        response.active_application_count
        == expected_professional.active_application_count
    )
    assert_filter_called_with(mock_query, Professional.id == td.VALID_PROFESSIONAL_ID)
    mock_db.query.assert_called_once_with(Professional)


def test_get_by_id_whenProfessionalNotFound(mock_db):
    # Arrange
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = None

    # Act
    with pytest.raises(ApplicationError) as exc:
        professional_service._get_by_id(
            professional_id=td.VALID_PROFESSIONAL_ID, db=mock_db
        )

    # Assert
    assert_filter_called_with(mock_query, Professional.id == td.VALID_PROFESSIONAL_ID)
    assert exc.value.data.status == status.HTTP_404_NOT_FOUND
    assert (
        exc.value.data.detail
        == f"Professional with id {td.VALID_PROFESSIONAL_ID} not found"
    )


def test_get_matches_whenDataIsValid(mocker, mock_db):
    # Arrange
    mock_job_ad_1 = mocker.Mock(**td.JOB_AD_1)
    mock_job_ad_2 = mocker.Mock(**td.JOB_AD_2)
    mock_job_ads = [mock_job_ad_1, mock_job_ad_2]

    mock_query = mock_db.query.return_value
    mock_join_1 = mock_query.join.return_value
    mock_join_2 = mock_join_1.join.return_value
    mock_filter = mock_join_2.filter.return_value
    mock_filter.all.return_value = mock_job_ads

    mock_job_ad_response_1 = JobAdPreview(
        **td.JOB_AD_1, city=City(**td.CITY), category_name=td.VALID_CATEGORY_TITLE
    )
    mock_job_ad_response_2 = JobAdPreview(
        **td.JOB_AD_2, city=City(**td.CITY_2), category_name=td.VALID_CATEGORY_TITLE_2
    )

    mocker.patch(
        "app.services.professional_service.JobAdPreview.create",
        side_effect=[mock_job_ad_response_1, mock_job_ad_response_2],
    )

    # Act
    response = professional_service._get_matches(
        professional_id=td.VALID_PROFESSIONAL_ID, db=mock_db
    )

    # Assert
    assert len(response) == 2
    assert response[0] == mock_job_ad_response_1
    assert response[1] == mock_job_ad_response_2
    mock_filter.all.assert_called_once()


def test_update_attributes_updatesStatus(mocker, mock_db):
    # Arrange
    mock_professional_request = mocker.Mock(
        professional=mocker.Mock(city=None),
        status="new_status",
    )
    mock_professional = mocker.Mock(status="old_status")

    mock_process_transaction = mocker.patch(
        "app.services.professional_service.process_db_transaction",
        side_effect=lambda transaction_func, db: transaction_func(),
    )

    # Act
    result = professional_service._update_attributes(
        professional_request=mock_professional_request,
        professional=mock_professional,
        db=mock_db,
    )

    # Assert
    assert result.status == "new_status"
    mock_process_transaction.assert_called_once()


def test_update_attributes_updatesCity(mocker, mock_db):
    # Arrange
    mock_professional_request = mocker.Mock(
        professional=mocker.Mock(city=td.VALID_CITY_NAME),
        status=None,
    )
    mock_professional = mocker.Mock(city=mocker.Mock(name="Old City"))

    mock_city = mocker.Mock(id=td.VALID_CITY_ID, name=td.VALID_CITY_NAME)
    mock_get_by_name = mocker.patch(
        "app.services.city_service.get_by_name", return_value=mock_city
    )
    mock_process_transaction = mocker.patch(
        "app.services.professional_service.process_db_transaction",
        side_effect=lambda transaction_func, db: transaction_func(),
    )

    # Act
    result = professional_service._update_attributes(
        professional_request=mock_professional_request,
        professional=mock_professional,
        db=mock_db,
    )

    # Assert
    assert result.city_id == td.VALID_CITY_ID
    mock_get_by_name.assert_called_once_with(city_name=td.VALID_CITY_NAME, db=mock_db)
    mock_process_transaction.assert_called_once()


def test_update_attributes_updatesDescription(mocker, mock_db):
    # Arrange
    mock_professional_request = mocker.Mock(
        professional=mocker.Mock(description="New Description", city=None),
        status=None,
    )
    mock_professional = mocker.Mock(description="Old Description")

    mock_process_transaction = mocker.patch(
        "app.services.professional_service.process_db_transaction",
        side_effect=lambda transaction_func, db: transaction_func(),
    )

    # Act
    result = professional_service._update_attributes(
        professional_request=mock_professional_request,
        professional=mock_professional,
        db=mock_db,
    )

    # Assert
    assert result.description == "New Description"
    mock_process_transaction.assert_called_once()


def test_update_attributes_updatesFirstName(mocker, mock_db):
    # Arrange
    mock_professional_request = mocker.Mock(
        professional=mocker.Mock(first_name="New Name", city=None),
        status=None,
    )
    mock_professional = mocker.Mock(first_name="Old Name")

    mock_process_transaction = mocker.patch(
        "app.services.professional_service.process_db_transaction",
        side_effect=lambda transaction_func, db: transaction_func(),
    )

    # Act
    result = professional_service._update_attributes(
        professional_request=mock_professional_request,
        professional=mock_professional,
        db=mock_db,
    )

    # Assert
    assert result.first_name == "New Name"
    mock_process_transaction.assert_called_once()


def test_update_attributes_updatesLastName(mocker, mock_db):
    # Arrange
    mock_professional_request = mocker.Mock(
        professional=mocker.Mock(last_name="New Last Name", city=None),
        status=None,
    )
    mock_professional = mocker.Mock(last_name="Old Last Name")

    mock_process_transaction = mocker.patch(
        "app.services.professional_service.process_db_transaction",
        side_effect=lambda transaction_func, db: transaction_func(),
    )

    # Act
    result = professional_service._update_attributes(
        professional_request=mock_professional_request,
        professional=mock_professional,
        db=mock_db,
    )

    # Assert
    assert result.last_name == "New Last Name"
    mock_process_transaction.assert_called_once()


def test_set_matches_status_private(mocker, mock_db):
    # Arrange
    professional_id = mocker.Mock()
    mock_professional = mocker.Mock(has_private_matches=False)

    mock_get_by_id = mocker.patch(
        "app.services.professional_service._get_by_id", return_value=mock_professional
    )
    mock_process_transaction = mocker.patch(
        "app.services.professional_service.process_db_transaction",
        side_effect=lambda transaction_func, db: transaction_func(),
    )

    private_matches = mocker.Mock(status=True)

    # Act
    result = professional_service.set_matches_status(
        professional_id=professional_id, db=mock_db, private_matches=private_matches
    )

    # Assert
    assert result == {"msg": "Matches set as private"}
    assert mock_professional.has_private_matches is True
    mock_get_by_id.assert_called_once_with(professional_id=professional_id, db=mock_db)
    mock_process_transaction.assert_called_once()


def test_set_matches_status_public(mocker, mock_db):
    # Arrange
    professional_id = mocker.Mock()
    mock_professional = mocker.Mock(has_private_matches=True)

    mock_get_by_id = mocker.patch(
        "app.services.professional_service._get_by_id", return_value=mock_professional
    )
    mock_process_transaction = mocker.patch(
        "app.services.professional_service.process_db_transaction",
        side_effect=lambda transaction_func, db: transaction_func(),
    )

    private_matches = mocker.Mock(status=False)

    # Act
    result = professional_service.set_matches_status(
        professional_id=professional_id, db=mock_db, private_matches=private_matches
    )

    # Assert
    assert result == {"msg": "Matches set as public"}
    assert mock_professional.has_private_matches is False
    mock_get_by_id.assert_called_once_with(professional_id=professional_id, db=mock_db)
    mock_process_transaction.assert_called_once()


def test_get_by_username_returns_user(mocker, mock_db):
    # Arrange
    mock_professional = mocker.Mock(
        id=td.VALID_PROFESSIONAL_ID,
        username=td.VALID_PROFESSIONAL_USERNAME,
        password=td.VALID_PROFESSIONAL_PASSWORD,
    )

    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = mock_professional

    expected_user = User(
        id=td.VALID_PROFESSIONAL_ID,
        username=td.VALID_PROFESSIONAL_USERNAME,
        password=td.VALID_PROFESSIONAL_PASSWORD,
    )

    # Act
    result = professional_service.get_by_username(
        username=td.VALID_PROFESSIONAL_USERNAME, db=mock_db
    )

    # Assert
    assert result.id == expected_user.id
    assert result.username == expected_user.username
    assert result.password == expected_user.password
    mock_db.query.assert_called_once_with(Professional)


def test_get_by_username_raises_error_when_user_not_found(mocker, mock_db):
    # Arrange
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = None

    # Act & Assert
    with pytest.raises(ApplicationError) as exc:
        professional_service.get_by_username(
            username=td.VALID_PROFESSIONAL_USERNAME, db=mock_db
        )

    assert (
        exc.value.data.detail
        == f"User with username {td.VALID_PROFESSIONAL_USERNAME} does not exist"
    )
    assert exc.value.data.status == status.HTTP_404_NOT_FOUND
    mock_db.query.assert_called_once_with(Professional)


def test_get_applications_private_matches_error(mocker, mock_db):
    # Arrange
    mock_professional = mocker.Mock(
        id=td.VALID_PROFESSIONAL_ID,
        has_private_matches=True,
    )

    mock_application_status = JobSearchStatus.MATCHED
    mock_filter_params = mocker.Mock(offset=0, limit=10)

    mock_get_by_id = mocker.patch(
        "app.services.professional_service._get_by_id", return_value=mock_professional
    )

    # Act & Assert
    with pytest.raises(
        ApplicationError, match="Professional has set their Matches to Private"
    ) as exc:
        professional_service.get_applications(
            professional_id=td.VALID_PROFESSIONAL_ID,
            db=mock_db,
            application_status=mock_application_status,
            filter_params=mock_filter_params,
        )

    mock_get_by_id.assert_called_once()
    assert exc.value.data.status == status.HTTP_403_FORBIDDEN
    assert exc.value.data.detail == "Professional has set their Matches to Private"


def test_get_applications_returns_list_of_applications(mocker, mock_db):
    # Arrange
    mock_professional = mocker.Mock(id=td.VALID_PROFESSIONAL_ID)
    mock_application_status = JobSearchStatus.ACTIVE
    mock_filter_params = mocker.Mock(offset=0, limit=10)

    mock_get_by_id = mocker.patch(
        "app.services.professional_service._get_by_id", return_value=mock_professional
    )

    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.offset.return_value = mock_filter
    mock_filter.limit.return_value = mock_filter
    mock_filter.all.return_value = [mocker.Mock(id=td.VALID_JOB_APPLICATION_ID)]

    mock_application_response = mocker.Mock()
    mocker.patch(
        "app.services.professional_service.JobApplicationResponse.create",
        return_value=mock_application_response,
    )

    # Act
    result = professional_service.get_applications(
        professional_id=td.VALID_PROFESSIONAL_ID,
        db=mock_db,
        application_status=mock_application_status,
        filter_params=mock_filter_params,
    )

    # Assert
    assert len(result) == 1
    assert result[0] == mock_application_response
    mock_get_by_id.assert_called_once()
    mock_db.query.assert_called_once_with(JobApplication)
    mock_query.filter.assert_called_once()
    mock_filter.offset.assert_called_once_with(0)
    mock_filter.limit.assert_called_once_with(10)


def test_get_applications_empty_list(mocker, mock_db):
    # Arrange
    mock_professional = mocker.Mock(id=td.VALID_PROFESSIONAL_ID)
    mock_application_status = JobSearchStatus.ACTIVE
    mock_filter_params = mocker.Mock(offset=0, limit=10)

    mock_get_by_id = mocker.patch(
        "app.services.professional_service._get_by_id", return_value=mock_professional
    )

    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.offset.return_value = mock_filter
    mock_filter.limit.return_value = mock_filter
    mock_filter.all.return_value = []

    # Act
    result = professional_service.get_applications(
        professional_id=td.VALID_PROFESSIONAL_ID,
        db=mock_db,
        application_status=mock_application_status,
        filter_params=mock_filter_params,
    )

    # Assert
    assert len(result) == 0
    mock_get_by_id.assert_called_once()
    mock_db.query.assert_called_once_with(JobApplication)
    mock_query.filter.assert_called_once()


def test_register_professional_username_taken(mocker, mock_db):
    # Arrange
    mock_professional_create = mocker.Mock(
        username=td.VALID_PROFESSIONAL_USERNAME,
        email=td.VALID_PROFESSIONAL_EMAIL,
        password=td.VALID_PROFESSIONAL_PASSWORD,
    )
    mock_professional_status = mocker.Mock()
    mock_city_id = mocker.Mock()

    mock_unique_username = mocker.patch(
        "app.services.professional_service.unique_username", return_value=False
    )

    # Act & Assert
    with pytest.raises(ApplicationError) as exc:
        professional_service._register_professional(
            professional_create=mock_professional_create,
            professional_status=mock_professional_status,
            city_id=mock_city_id,
            db=mock_db,
        )

    mock_unique_username.assert_called_once_with(
        username=td.VALID_PROFESSIONAL_USERNAME, db=mock_db
    )
    assert exc.value.data.status == status.HTTP_409_CONFLICT
    assert exc.value.data.detail == "Username already taken"


def test_register_professional_email_taken(mocker, mock_db):
    # Arrange
    mock_professional_create = mocker.Mock(
        username=td.VALID_PROFESSIONAL_USERNAME,
        email=td.VALID_PROFESSIONAL_EMAIL,
        password=td.VALID_PROFESSIONAL_PASSWORD,
    )
    mock_professional_status = mocker.Mock()
    mock_city_id = mocker.Mock()

    mock_unique_username = mocker.patch(
        "app.services.professional_service.unique_username", return_value=True
    )
    mock_unique_email = mocker.patch(
        "app.services.professional_service.unique_email", return_value=False
    )

    # Act & Assert
    with pytest.raises(ApplicationError) as exc:
        professional_service._register_professional(
            professional_create=mock_professional_create,
            professional_status=mock_professional_status,
            city_id=mock_city_id,
            db=mock_db,
        )

    mock_unique_username.assert_called_once_with(
        username=td.VALID_PROFESSIONAL_USERNAME, db=mock_db
    )
    mock_unique_email.assert_called_once_with(
        email=td.VALID_PROFESSIONAL_EMAIL, db=mock_db
    )
    assert exc.value.data.status == status.HTTP_409_CONFLICT
    assert exc.value.data.detail == "Email already taken"


def test_register_professional_successful(mocker, mock_db):
    # Arrange
    mock_professional_create = mocker.Mock(
        username=td.VALID_PROFESSIONAL_USERNAME,
        email=td.VALID_PROFESSIONAL_EMAIL,
        password=td.VALID_PROFESSIONAL_PASSWORD,
    )
    mock_professional_status = mocker.Mock()
    mock_city_id = mocker.Mock()

    mock_unique_username = mocker.patch(
        "app.services.professional_service.unique_username", return_value=True
    )
    mock_unique_email = mocker.patch(
        "app.services.professional_service.unique_email", return_value=True
    )
    mock_hash_password = mocker.patch(
        "app.services.professional_service.hash_password",
        return_value="hashed_password",
    )
    mock_create = mocker.patch(
        "app.services.professional_service._create", return_value="new_professional"
    )

    # Act
    result = professional_service._register_professional(
        professional_create=mock_professional_create,
        professional_status=mock_professional_status,
        city_id=mock_city_id,
        db=mock_db,
    )

    # Assert
    assert result == "new_professional"
    mock_unique_username.assert_called_once_with(
        username=td.VALID_PROFESSIONAL_USERNAME, db=mock_db
    )
    mock_unique_email.assert_called_once_with(
        email=td.VALID_PROFESSIONAL_EMAIL, db=mock_db
    )
    mock_hash_password.assert_called_once_with(password=td.VALID_PROFESSIONAL_PASSWORD)
    mock_create.assert_called_once_with(
        professional_create=mock_professional_create,
        city_id=mock_city_id,
        professional_status=mock_professional_status,
        hashed_password="hashed_password",
        db=mock_db,
    )


def test_create_professional_success(mocker, mock_db):
    # Arrange
    mock_professional_create = mocker.MagicMock()
    mock_professional_create.username = td.VALID_PROFESSIONAL_USERNAME
    mock_professional_create.email = td.VALID_PROFESSIONAL_EMAIL
    mock_professional_create.password = td.VALID_PROFESSIONAL_PASSWORD
    mock_professional_create.model_dump.return_value = {
        "username": td.VALID_PROFESSIONAL_USERNAME,
        "email": td.VALID_PROFESSIONAL_EMAIL,
    }

    mock_professional_status = mocker.Mock()
    mock_city_id = mocker.Mock()
    mock_hashed_password = "hashed_password"

    mock_professional = mocker.MagicMock(spec=Professional)
    mock_professional.id = td.VALID_PROFESSIONAL_ID

    mock_db.add = mocker.MagicMock()
    mock_db.commit = mocker.MagicMock()
    mock_db.refresh = mocker.MagicMock()

    def mock_process_db_transaction(transaction_func, db):
        print("Inside mock_process_db_transaction")
        return transaction_func()

    mock_process_db_transaction = mocker.patch(
        "app.services.professional_service.process_db_transaction",
        side_effect=mock_process_db_transaction,
    )

    mocker.patch(
        "app.services.professional_service.Professional", return_value=mock_professional
    )

    # Act
    result = professional_service._create(
        professional_create=mock_professional_create,
        city_id=mock_city_id,
        professional_status=mock_professional_status,
        hashed_password=mock_hashed_password,
        db=mock_db,
    )

    # Assert
    mock_process_db_transaction.assert_called_once()
    mock_db.add.assert_called_once_with(mock_professional)
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(mock_professional)
    assert result == mock_professional


def test_upload_cv_successful(mocker, mock_db):
    # Arrange
    professional_id = td.VALID_PROFESSIONAL_ID
    mock_professional = mocker.Mock()
    mock_get_by_id = mocker.patch(
        "app.services.professional_service._get_by_id", return_value=mock_professional
    )
    mock_handle_file_upload = mocker.patch(
        "app.services.professional_service.handle_file_upload",
        return_value=td.VALID_CV_PATH,
    )
    mock_commit = mocker.patch.object(mock_db, "commit")

    mock_cv = mocker.Mock()
    mock_cv.content_type = "application/pdf"

    # Act
    result = professional_service.upload_cv(
        professional_id=professional_id, cv=mock_cv, db=mock_db
    )

    # Assert
    mock_get_by_id.assert_called_once_with(professional_id=professional_id, db=mock_db)
    mock_handle_file_upload.assert_called_once_with(file_to_upload=mock_cv)
    mock_commit.assert_called_once()
    assert mock_professional.cv == td.VALID_CV_PATH
    assert "msg" in result
    assert result["msg"] == "CV successfully uploaded"


def test_upload_cv_invalid_file_type(mocker, mock_db):
    # Arrange
    professional_id = td.VALID_PROFESSIONAL_ID
    mock_professional = mocker.Mock()
    mocker.patch(
        "app.services.professional_service._get_by_id", return_value=mock_professional
    )

    mock_cv = mocker.Mock()
    mock_cv.content_type = "text/plain"

    # Act & Assert
    with pytest.raises(ApplicationError) as exc:
        professional_service.upload_cv(
            professional_id=professional_id, cv=mock_cv, db=mock_db
        )

    assert exc.value.data.status == status.HTTP_400_BAD_REQUEST
    assert exc.value.data.detail == "Only PDF files are allowed."


def test_upload_cv_updates_professional(mocker, mock_db):
    # Arrange
    professional_id = td.VALID_PROFESSIONAL_ID
    mock_professional = mocker.Mock()
    mocker.patch(
        "app.services.professional_service._get_by_id", return_value=mock_professional
    )
    mock_handle_file_upload = mocker.patch(
        "app.services.professional_service.handle_file_upload",
        return_value=td.VALID_CV_PATH,
    )
    mock_commit = mocker.patch.object(mock_db, "commit")

    mock_cv = mocker.Mock()
    mock_cv.content_type = "application/pdf"
    old_updated_at = mock_professional.updated_at

    # Act
    professional_service.upload_cv(
        professional_id=professional_id, cv=mock_cv, db=mock_db
    )

    # Assert
    mock_handle_file_upload.assert_called_once_with(file_to_upload=mock_cv)
    mock_commit.assert_called_once()
    assert mock_professional.cv == td.VALID_CV_PATH
    assert mock_professional.updated_at != old_updated_at


def test_download_cv_successful(mocker, mock_db):
    # Arrange
    professional_id = td.VALID_PROFESSIONAL_ID
    mock_professional = mocker.Mock()
    mock_professional.cv = b"PDF content"
    mock_professional.first_name = td.VALID_PROFESSIONAL_FIRST_NAME
    mock_professional.last_name = td.VALID_PROFESSIONAL_LAST_NAME

    mock_get_by_id = mocker.patch(
        "app.services.professional_service._get_by_id", return_value=mock_professional
    )

    # Act
    response = professional_service.download_cv(
        professional_id=professional_id, db=mock_db
    )

    # Assert
    mock_get_by_id.assert_called_once_with(professional_id=professional_id, db=mock_db)
    assert isinstance(response, StreamingResponse)
    assert response.media_type == "application/pdf"
    assert (
        response.headers["Content-Disposition"]
        == "attachment; filename=Test_Professional_CV.pdf"
    )
    assert response.headers["Access-Control-Expose-Headers"] == "Content-Disposition"


def test_download_cv_no_cv(mocker, mock_db):
    # Arrange
    professional_id = td.VALID_PROFESSIONAL_ID
    mock_professional = mocker.Mock()
    mock_professional.cv = None
    mocker.patch(
        "app.services.professional_service._get_by_id", return_value=mock_professional
    )

    # Act
    response = professional_service.download_cv(
        professional_id=professional_id, db=mock_db
    )

    # Assert
    assert isinstance(response, JSONResponse)
    assert response.status_code == 200


def test_delete_cv_success(mocker, mock_db):
    # Arrange
    professional_id = td.VALID_PROFESSIONAL_ID
    mock_professional = mocker.Mock()
    mock_professional.cv = b"some_cv_data"
    mock_professional.updated_at = None
    mocker.patch(
        "app.services.professional_service._get_by_id", return_value=mock_professional
    )

    mock_commit = mocker.patch.object(mock_db, "commit")

    # Act
    response = professional_service.delete_cv(
        professional_id=professional_id, db=mock_db
    )

    # Assert
    assert isinstance(response, MessageResponse)
    assert response.message == "CV deleted successfully"
    assert mock_professional.cv is None
    assert mock_professional.updated_at is not None
    mock_commit.assert_called_once()
