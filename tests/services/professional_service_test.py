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
