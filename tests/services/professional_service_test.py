import json

import pytest
from fastapi import status

from app.exceptions.custom_exceptions import ApplicationError
from app.services import professional_service
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


def test_upload_whenFileIsValid(mocker, mock_db):
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
    result = professional_service.upload(
        professional_id=professional_id, photo=mock_upload_file, db=mock_db
    )

    # Assert
    mock_get_by_id.assert_called_once_with(professional_id=professional_id, db=mock_db)
    mock_upload_file.file.read.assert_called_once()
    mock_upload_file.file.seek.assert_called_once_with(0)
    mock_process_db_transaction.assert_called_once()
    assert mock_professional.photo == mock_file_content
    assert result == {"msg": "Photo successfully uploaded"}


def test_upload_whenFileExceedsSizeLimit(mocker, mock_db):
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
        professional_service.upload(
            professional_id=professional_id, photo=mock_upload_file, db=mock_db
        )

    assert exc.value.data.detail == "File size exceeds the allowed limit of 5.0MB."
    assert exc.value.data.status == status.HTTP_400_BAD_REQUEST


def test_download_whenPhotoExists(mocker, mock_db):
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
    response = professional_service.download(
        professional_id=professional_id, db=mock_db
    )

    # Assert
    assert response.status_code == 200
    assert response.media_type == "image/png"
    mock_get_by_id.assert_called_once_with(professional_id=professional_id, db=mock_db)


def test_download_whenPhotoIsNone(mocker, mock_db):
    # Arrange
    professional_id = td.VALID_PROFESSIONAL_ID
    mock_professional = mocker.Mock()
    mock_professional.photo = None

    mock_get_by_id = mocker.patch(
        "app.services.professional_service._get_by_id",
        return_value=mock_professional,
    )

    # Act
    response = professional_service.download(
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


def test_get_all_whenProfessionalsFilteredBySkills(mocker, mock_db):
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
    mock_filtered_by_skills = mock_filtered_by_status.filter.return_value
    mock_offset = mock_filtered_by_skills.offset.return_value
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
    assert response.active_application_count == expected_professional.active_application_count
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
    assert exc.value.data.detail == f"Professional with id {td.VALID_PROFESSIONAL_ID} not found"