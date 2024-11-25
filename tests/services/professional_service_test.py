import pytest
from fastapi import status

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.professional import ProfessionalCreate, ProfessionalRequestBody
from app.services import professional_service
from app.sql_app.professional.professional_status import ProfessionalStatus
from tests import test_data as td


@pytest.fixture
def mock_db(mocker):
    return mocker.Mock()


def test_create_raises_error_when_city_not_found(mocker, mock_db) -> None:
    # Arrange
    professional_request = ProfessionalRequestBody(
        professional=ProfessionalCreate(
            username=td.VALID_PROFESSIONAL_USERNAME,
            password=td.VALID_PROFESSIONAL_PASSWORD,
            email=td.VALID_PROFESSIONAL_EMAIL,
            first_name=td.VALID_PROFESSIONAL_FIRST_NAME,
            last_name=td.VALID_PROFESSIONAL_LAST_NAME,
            description=td.VALID_PROFESSIONAL_DESCRIPTION,
            city=td.VALID_CITY_NAME,
        ),
        status=ProfessionalStatus.ACTIVE,
    )
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
