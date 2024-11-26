import pytest
from fastapi import status

from app.exceptions.custom_exceptions import ApplicationError
from app.services import professional_service
from tests import test_data as td


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
    professional_mock = mocker.Mock(**td.PROFESSIONAL)
    response_mock = mocker.Mock(**td.PROFESSIONAL)

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
        side_effect=lambda transaction_func, db: transaction_func()
    )

    oversized_content = b"a" * (5 * 1024 * 1024 + 1)
    mock_upload_file = mocker.Mock()
    mock_upload_file.file.read.return_value = oversized_content
    mock_upload_file.file.seek.return_value = None

    # Act & Assert
    with pytest.raises(ApplicationError) as exc:
        professional_service.upload(professional_id=professional_id, photo=mock_upload_file, db=mock_db)

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
    response = professional_service.download(professional_id=professional_id, db=mock_db)

    # Assert
    assert response.status_code == 200
    assert response.media_type == "image/png"
    mock_get_by_id.assert_called_once_with(professional_id=professional_id, db=mock_db)
