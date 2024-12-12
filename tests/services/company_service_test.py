import pytest
from fastapi import status

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.company import CompanyUpdate
from app.services import company_service
from app.services.external_db_service_urls import (
    COMPANIES_URL,
    COMPANY_BY_ID_URL,
    COMPANY_BY_USERNAME_URL,
    COMPANY_LOGO_URL,
)
from tests import test_data as td


def test_getAll_returnsCompanies_whenCompaniesAreFound(mocker) -> None:
    # Arrange
    companies = [td.COMPANY, td.COMPANY_2]
    mock_filter_params = mocker.Mock(offset=0, limit=10)
    mock_response = [mocker.Mock(), mocker.Mock()]

    mock_perform_get_request = mocker.patch(
        "app.services.company_service.perform_get_request",
        return_value=companies,
    )
    mock_response_init = mocker.patch(
        "app.services.company_service.CompanyResponse",
        side_effect=mock_response,
    )

    # Act
    result = company_service.get_all(filter_params=mock_filter_params)

    # Assert
    mock_perform_get_request.assert_called_with(
        url=COMPANIES_URL, params=mock_filter_params.model_dump()
    )
    mock_response_init.assert_has_calls(
        [mocker.call(**companies[0]), mocker.call(**companies[1])]
    )
    assert len(result) == 2
    assert result[0] == mock_response[0]
    assert result[1] == mock_response[1]


def test_getAll_returnsEmptyList_whenNoCompaniesAreFound(mocker) -> None:
    # Arrange
    mock_filter_params = mocker.Mock(offset=0, limit=10)
    mock_perform_get_request = mocker.patch(
        "app.services.company_service.perform_get_request",
        return_value=[],
    )

    # Act
    result = company_service.get_all(filter_params=mock_filter_params)

    # Assert
    mock_perform_get_request.assert_called_with(
        url=COMPANIES_URL, params=mock_filter_params.model_dump()
    )
    assert len(result) == 0


def test_getById_returnsCompany_whenCompanyIsFound(mocker) -> None:
    # Arrange
    company = td.COMPANY
    mock_response = mocker.Mock()

    mock_perform_get_request = mocker.patch(
        "app.services.company_service.perform_get_request",
        return_value=company,
    )
    mock_response_init = mocker.patch(
        "app.services.company_service.CompanyResponse",
        return_value=mock_response,
    )

    # Act
    result = company_service.get_by_id(company_id=td.VALID_COMPANY_ID)

    # Assert
    mock_perform_get_request.assert_called_with(
        url=COMPANY_BY_ID_URL.format(company_id=td.VALID_COMPANY_ID)
    )
    mock_response_init.assert_called_with(**company)
    assert result == mock_response


def test_getByUsername_returnsUser_whenUserIsFound(mocker) -> None:
    # Arrange
    user = {
        "id": td.VALID_COMPANY_ID,
        "username": td.VALID_COMPANY_USERNAME,
        "password": td.VALID_PASSWORD,
    }
    mock_response = mocker.Mock()

    mock_perform_get_request = mocker.patch(
        "app.services.company_service.perform_get_request",
        return_value=user,
    )
    mock_response_init = mocker.patch(
        "app.services.company_service.User",
        return_value=mock_response,
    )

    # Act
    result = company_service.get_by_username(username=td.VALID_COMPANY_USERNAME)

    # Assert
    mock_perform_get_request.assert_called_with(
        url=COMPANY_BY_USERNAME_URL.format(username=td.VALID_COMPANY_USERNAME)
    )
    mock_response_init.assert_called_with(**user)
    assert result == mock_response


def test_create_createsCompany_whenDataIsValid(mocker) -> None:
    # Arrange
    mock_company = mocker.Mock(id=td.VALID_COMPANY_ID)
    mock_company_data = mocker.Mock()
    mock_company_data.model_dump.return_value = {}
    mock_city = mocker.Mock(id=td.VALID_CITY_ID)
    mock_response = mocker.MagicMock(id=td.VALID_COMPANY_ID)

    mock_ensure_valid_company_creation_data = mocker.patch(
        "app.services.company_service._ensure_valid_company_creation_data"
    )
    mock_ensure_valid_city = mocker.patch(
        "app.services.company_service.ensure_valid_city",
        return_value=mock_city,
    )
    mock_hash_password = mocker.patch(
        "app.services.company_service.hash_password",
        return_value=td.HASHED_PASSWORD,
    )
    mock_perform_post_request = mocker.patch(
        "app.services.company_service.perform_post_request",
        return_value=mock_response,
    )
    mock_company_response = mocker.patch(
        "app.services.company_service.CompanyResponse",
        return_value=mock_response,
    )
    mock_company_create_final = mocker.patch(
        "app.services.company_service.CompanyCreateFinal",
        return_value=mock_company,
    )
    mock_send_mail = mocker.patch("app.services.company_service.get_mail_service")

    # Act
    result = company_service.create(company_data=mock_company_data)

    # Assert
    mock_ensure_valid_company_creation_data.assert_called_with(
        company_data=mock_company_data
    )
    mock_ensure_valid_city.assert_called_with(name=mock_company_data.city)
    mock_hash_password.assert_called_with(mock_company_data.password)
    mock_perform_post_request.assert_called_once()
    mock_company_response.assert_called_once()
    assert result == mock_response


def test_update_updatesCompany_whenDataIsValid(mocker) -> None:
    # Arrange
    company_id = td.VALID_COMPANY_ID
    company_data = CompanyUpdate(
        name=td.VALID_COMPANY_NAME_2,
        email=td.VALID_COMPANY_EMAIL_2,
        phone_number=td.VALID_COMPANY_PHONE_NUMBER_2,
        city=td.VALID_CITY_NAME_2,
    )
    mock_company = mocker.Mock(id=company_id)
    mock_city = mocker.Mock(id=td.VALID_CITY_ID_2)
    mock_response = mocker.MagicMock(id=td.VALID_COMPANY_ID)

    mock_ensure_valid_company_id = mocker.patch(
        "app.services.company_service.ensure_valid_company_id",
        return_value=mock_company,
    )
    mock_ensure_valid_city = mocker.patch(
        "app.services.company_service.ensure_valid_city",
        return_value=mock_city,
    )
    mock_ensure_unique_email = mocker.patch(
        "app.services.company_service._ensure_unique_email"
    )
    mock_ensure_unique_phone_number = mocker.patch(
        "app.services.company_service._ensure_unique_phone_number"
    )
    mock_perform_put_request = mocker.patch(
        "app.services.company_service.perform_put_request",
        return_value=mock_response,
    )
    mock_company_response = mocker.patch(
        "app.services.company_service.CompanyResponse",
        return_value=mock_response,
    )

    # Act
    result = company_service.update(company_id=company_id, company_data=company_data)

    # Assert
    mock_ensure_valid_company_id.assert_called_with(company_id=company_id)
    mock_ensure_valid_city.assert_called_with(name=company_data.city)
    mock_ensure_unique_email.assert_called_with(email=company_data.email)
    mock_ensure_unique_phone_number.assert_called_with(
        phone_number=company_data.phone_number
    )
    mock_perform_put_request.assert_called_once()
    mock_company_response.assert_called_once()
    assert result == mock_response


def test_uploadLogo_uploadsLogo_whenDataIsValid(mocker) -> None:
    # Arrange
    company_id = td.VALID_COMPANY_ID
    mock_logo = mocker.Mock()
    mock_logo.filename = "logo.png"
    mock_logo.file = mocker.Mock()
    mock_logo.content_type = "image/png"
    mock_message_response = mocker.Mock(message="Logo uploaded successfully")

    mock_validate_uploaded_file = mocker.patch(
        "app.services.company_service.validate_uploaded_file"
    )
    mock_perform_post_request = mocker.patch(
        "app.services.company_service.perform_post_request",
        return_value=mock_message_response,
    )
    mock_message_response_init = mocker.patch(
        "app.services.company_service.MessageResponse",
        return_value=mock_message_response,
    )

    # Act
    result = company_service.upload_logo(company_id=company_id, logo=mock_logo)

    # Assert
    mock_validate_uploaded_file.assert_called_with(mock_logo)
    mock_perform_post_request.assert_called_with(
        url=COMPANY_LOGO_URL.format(company_id=company_id),
        files={"logo": (mock_logo.filename, mock_logo.file, mock_logo.content_type)},
    )
    mock_message_response_init.assert_called_once()
    assert result == mock_message_response


def test_downloadLogo_returnsLogo_whenDataIsValid(mocker) -> None:
    # Arrange
    company_id = td.VALID_COMPANY_ID
    mock_logo_content = b"logo content"
    mock_response = mocker.Mock()
    mock_response.content = mock_logo_content

    mock_ensure_valid_company_id = mocker.patch(
        "app.services.company_service.ensure_valid_company_id"
    )
    mock_perform_get_request = mocker.patch(
        "app.services.company_service.perform_get_request",
        return_value=mock_response,
    )
    mock_streaming_response = mocker.patch(
        "app.services.company_service.StreamingResponse",
        return_value=mock_response,
    )

    # Act
    result = company_service.download_logo(company_id=company_id)

    # Assert
    mock_ensure_valid_company_id.assert_called_with(company_id=company_id)
    mock_perform_get_request.assert_called_with(
        url=COMPANY_LOGO_URL.format(company_id=company_id)
    )
    assert result == mock_response


def test_deleteLogo_deletesLogo_whenDataIsValid(mocker) -> None:
    # Arrange
    company_id = td.VALID_COMPANY_ID
    mock_message_response = mocker.Mock(message="Logo deleted successfully")

    mock_ensure_valid_company_id = mocker.patch(
        "app.services.company_service.ensure_valid_company_id"
    )
    mock_perform_delete_request = mocker.patch(
        "app.services.company_service.perform_delete_request",
        return_value=mock_message_response,
    )
    mock_message_response_init = mocker.patch(
        "app.services.company_service.MessageResponse",
        return_value=mock_message_response,
    )

    # Act
    result = company_service.delete_logo(company_id=company_id)

    # Assert
    mock_ensure_valid_company_id.assert_called_with(company_id=company_id)
    mock_perform_delete_request.assert_called_with(
        url=COMPANY_LOGO_URL.format(company_id=company_id)
    )
    mock_message_response_init.assert_called_once()
    assert result == mock_message_response


def test_ensureUniqueEmail_raisesError_whenEmailIsNotUnique(mocker) -> None:
    # Arrange
    email = td.VALID_COMPANY_EMAIL
    mock_is_unique_email = mocker.patch(
        "app.services.company_service.is_unique_email",
        return_value=False,
    )

    # Act & Assert
    with pytest.raises(ApplicationError) as exc_info:
        company_service._ensure_unique_email(email=email)

    assert exc_info.value.data.status == status.HTTP_409_CONFLICT
    assert exc_info.value.data.detail == f"Company with email {email} already exists"
    mock_is_unique_email.assert_called_with(email=email)


def test_ensureUniqueEmail_doesNotRaiseError_whenEmailIsUnique(mocker) -> None:
    # Arrange
    email = td.VALID_COMPANY_EMAIL
    mock_is_unique_email = mocker.patch(
        "app.services.company_service.is_unique_email",
        return_value=True,
    )

    # Act
    company_service._ensure_unique_email(email=email)

    # Assert
    mock_is_unique_email.assert_called_with(email=email)


def test_ensureUniquePhoneNumber_raisesError_whenPhoneNumberIsNotUnique(mocker) -> None:
    # Arrange
    phone_number = td.VALID_COMPANY_PHONE_NUMBER
    mock_get_company_by_phone_number = mocker.patch(
        "app.services.company_service.get_company_by_phone_number",
        return_value=td.COMPANY,
    )

    # Act & Assert
    with pytest.raises(ApplicationError) as exc_info:
        company_service._ensure_unique_phone_number(phone_number=phone_number)

    assert exc_info.value.data.status == status.HTTP_409_CONFLICT
    assert (
        exc_info.value.data.detail
        == f"Company with phone number {phone_number} already exists"
    )
    mock_get_company_by_phone_number.assert_called_with(phone_number=phone_number)


def test_ensureUniquePhoneNumber_doesNotRaiseError_whenPhoneNumberIsUnique(
    mocker,
) -> None:
    # Arrange
    phone_number = td.VALID_COMPANY_PHONE_NUMBER
    mock_get_company_by_phone_number = mocker.patch(
        "app.services.company_service.get_company_by_phone_number",
        return_value=None,
    )

    # Act
    company_service._ensure_unique_phone_number(phone_number=phone_number)

    # Assert
    mock_get_company_by_phone_number.assert_called_with(phone_number=phone_number)


def test_ensureValidCompanyCreationData_callsValidators_whenDataIsValid(mocker) -> None:
    # Arrange
    company_data = mocker.Mock(
        username=td.VALID_COMPANY_USERNAME,
        email=td.VALID_COMPANY_EMAIL,
        phone_number=td.VALID_COMPANY_PHONE_NUMBER,
    )
    mock_is_unique_username = mocker.patch(
        "app.services.company_service.is_unique_username"
    )
    mock_is_unique_email = mocker.patch("app.services.company_service.is_unique_email")
    mock_ensure_unique_phone_number = mocker.patch(
        "app.services.company_service._ensure_unique_phone_number"
    )

    # Act
    company_service._ensure_valid_company_creation_data(company_data=company_data)

    # Assert
    mock_is_unique_username.assert_called_with(username=company_data.username)
    mock_is_unique_email.assert_called_with(email=company_data.email)
    mock_ensure_unique_phone_number.assert_called_with(
        phone_number=company_data.phone_number
    )


def test_ensureValidCompanyUpdateData_callsValidators_whenDataIsValid(mocker) -> None:
    # Arrange
    company_id = td.VALID_COMPANY_ID
    company_data = CompanyUpdate(
        name=td.VALID_COMPANY_NAME_2,
        email=td.VALID_COMPANY_EMAIL_2,
        phone_number=td.VALID_COMPANY_PHONE_NUMBER_2,
        city=td.VALID_CITY_NAME_2,
    )
    mock_company = mocker.Mock(
        id=company_id,
        email=td.VALID_COMPANY_EMAIL,
        phone_number=td.VALID_COMPANY_PHONE_NUMBER,
    )
    mock_city = mocker.Mock(id=td.VALID_CITY_ID_2)

    mock_ensure_valid_company_id = mocker.patch(
        "app.services.company_service.ensure_valid_company_id",
        return_value=mock_company,
    )
    mock_ensure_valid_city = mocker.patch(
        "app.services.company_service.ensure_valid_city",
        return_value=mock_city,
    )
    mock_ensure_unique_email = mocker.patch(
        "app.services.company_service._ensure_unique_email"
    )
    mock_ensure_unique_phone_number = mocker.patch(
        "app.services.company_service._ensure_unique_phone_number"
    )

    # Act
    result = company_service._ensure_valid_company_update_data(
        company_id=company_id, company_data=company_data
    )

    # Assert
    mock_ensure_valid_company_id.assert_called_with(company_id=company_id)
    mock_ensure_valid_city.assert_called_with(name=company_data.city)
    mock_ensure_unique_email.assert_called_with(email=company_data.email)
    mock_ensure_unique_phone_number.assert_called_with(
        phone_number=company_data.phone_number
    )
    assert result.city_id == mock_city.id


def test_ensureValidCompanyUpdateData_doesNotCallCityValidator_whenCityIsNone(
    mocker,
) -> None:
    # Arrange
    company_id = td.VALID_COMPANY_ID
    company_data = CompanyUpdate(
        name=td.VALID_COMPANY_NAME_2,
        email=td.VALID_COMPANY_EMAIL_2,
        phone_number=td.VALID_COMPANY_PHONE_NUMBER_2,
        city=None,
    )
    mock_company = mocker.Mock(
        id=company_id,
        email=td.VALID_COMPANY_EMAIL,
        phone_number=td.VALID_COMPANY_PHONE_NUMBER,
    )

    mock_ensure_valid_company_id = mocker.patch(
        "app.services.company_service.ensure_valid_company_id",
        return_value=mock_company,
    )
    mock_ensure_valid_city = mocker.patch(
        "app.services.company_service.ensure_valid_city"
    )
    mock_ensure_unique_email = mocker.patch(
        "app.services.company_service._ensure_unique_email"
    )
    mock_ensure_unique_phone_number = mocker.patch(
        "app.services.company_service._ensure_unique_phone_number"
    )

    # Act
    result = company_service._ensure_valid_company_update_data(
        company_id=company_id, company_data=company_data
    )

    # Assert
    mock_ensure_valid_company_id.assert_called_with(company_id=company_id)
    mock_ensure_valid_city.assert_not_called()
    mock_ensure_unique_email.assert_called_with(email=company_data.email)
    mock_ensure_unique_phone_number.assert_called_with(
        phone_number=company_data.phone_number
    )
    assert result.city_id is None


def test_ensureValidCompanyUpdateData_doesNotCallEmailValidator_whenEmailIsSame(
    mocker,
) -> None:
    # Arrange
    company_id = td.VALID_COMPANY_ID
    company_data = CompanyUpdate(
        name=td.VALID_COMPANY_NAME_2,
        email=td.VALID_COMPANY_EMAIL,
        phone_number=td.VALID_COMPANY_PHONE_NUMBER_2,
        city=td.VALID_CITY_NAME_2,
    )
    mock_company = mocker.Mock(
        id=company_id,
        email=td.VALID_COMPANY_EMAIL,
        phone_number=td.VALID_COMPANY_PHONE_NUMBER,
    )
    mock_city = mocker.Mock(id=td.VALID_CITY_ID_2)

    mock_ensure_valid_company_id = mocker.patch(
        "app.services.company_service.ensure_valid_company_id",
        return_value=mock_company,
    )
    mock_ensure_valid_city = mocker.patch(
        "app.services.company_service.ensure_valid_city",
        return_value=mock_city,
    )
    mock_ensure_unique_email = mocker.patch(
        "app.services.company_service._ensure_unique_email"
    )
    mock_ensure_unique_phone_number = mocker.patch(
        "app.services.company_service._ensure_unique_phone_number"
    )

    # Act
    result = company_service._ensure_valid_company_update_data(
        company_id=company_id, company_data=company_data
    )

    # Assert
    mock_ensure_valid_company_id.assert_called_with(company_id=company_id)
    mock_ensure_valid_city.assert_called_with(name=company_data.city)
    mock_ensure_unique_email.assert_not_called()
    mock_ensure_unique_phone_number.assert_called_with(
        phone_number=company_data.phone_number
    )
    assert result.city_id == mock_city.id


def test_ensureValidCompanyUpdateData_doesNotCallPhoneNumberValidator_whenPhoneNumberIsSame(
    mocker,
) -> None:
    # Arrange
    company_id = td.VALID_COMPANY_ID
    company_data = CompanyUpdate(
        name=td.VALID_COMPANY_NAME_2,
        email=td.VALID_COMPANY_EMAIL_2,
        phone_number=td.VALID_COMPANY_PHONE_NUMBER,
        city=td.VALID_CITY_NAME_2,
    )
    mock_company = mocker.Mock(
        id=company_id,
        email=td.VALID_COMPANY_EMAIL,
        phone_number=td.VALID_COMPANY_PHONE_NUMBER,
    )
    mock_city = mocker.Mock(id=td.VALID_CITY_ID_2)

    mock_ensure_valid_company_id = mocker.patch(
        "app.services.company_service.ensure_valid_company_id",
        return_value=mock_company,
    )
    mock_ensure_valid_city = mocker.patch(
        "app.services.company_service.ensure_valid_city",
        return_value=mock_city,
    )
    mock_ensure_unique_email = mocker.patch(
        "app.services.company_service._ensure_unique_email"
    )
    mock_ensure_unique_phone_number = mocker.patch(
        "app.services.company_service._ensure_unique_phone_number"
    )

    # Act
    result = company_service._ensure_valid_company_update_data(
        company_id=company_id, company_data=company_data
    )

    # Assert
    mock_ensure_valid_company_id.assert_called_with(company_id=company_id)
    mock_ensure_valid_city.assert_called_with(name=company_data.city)
    mock_ensure_unique_email.assert_called_with(email=company_data.email)
    mock_ensure_unique_phone_number.assert_not_called()
    assert result.city_id == mock_city.id
