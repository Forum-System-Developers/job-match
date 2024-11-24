from datetime import datetime
from unittest.mock import ANY
from uuid import UUID

import pytest
from fastapi import status

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.common import MessageResponse
from app.schemas.company import CompanyUpdate
from app.services import company_service
from app.sql_app.company.company import Company
from tests import test_data as td
from tests.utils import assert_filter_called_with


@pytest.fixture
def mock_db(mocker):
    return mocker.Mock()


def create_mock_company_dto(
    mocker,
    *,
    id: UUID | None = None,
    company_name: str | None = None,
    description: str | None = None,
    address_line: str | None = None,
    city: str | None = None,
    email: str | None = None,
    phone_number: str | None = None,
):
    return mocker.Mock(
        id=id,
        company_name=company_name,
        description=description,
        address_line=address_line,
        city=city,
        email=email,
        phone_number=phone_number,
    )


def test_getAll_returnsCompanies_whenCompaniesAreFound(
    mocker,
    mock_db,
) -> None:
    # Arrange
    mock_filter_params = mocker.Mock(offset=0, limit=10)
    mock_companies = [mocker.Mock(), mocker.Mock()]
    mock_company_response = [mocker.Mock(), mocker.Mock()]

    mock_query = mock_db.query.return_value
    mock_offset = mock_query.offset.return_value
    mock_limit = mock_offset.limit.return_value
    mock_limit.all.return_value = mock_companies

    mock_create = mocker.patch(
        "app.schemas.company.CompanyResponse.create",
        side_effect=mock_company_response,
    )

    # Act
    result = company_service.get_all(filter_params=mock_filter_params, db=mock_db)

    # Assert
    mock_db.query.assert_called_with(Company)
    mock_query.offset.assert_called_with(mock_filter_params.offset)
    mock_offset.limit.assert_called_with(mock_filter_params.limit)
    mock_create.assert_any_call(mock_companies[0])
    mock_create.assert_any_call(mock_companies[1])
    assert len(result) == 2
    assert result[0] == mock_company_response[0]
    assert result[1] == mock_company_response[1]


def test_getAll_returnsEmptyList_whenNoCompaniesAreFound(
    mocker,
    mock_db,
) -> None:
    # Arrange
    mock_filter_params = mocker.Mock(offset=0, limit=10)

    mock_query = mock_db.query.return_value
    mock_offset = mock_query.offset.return_value
    mock_limit = mock_offset.limit.return_value
    mock_limit.all.return_value = []

    # Act
    result = company_service.get_all(filter_params=mock_filter_params, db=mock_db)

    # Assert
    mock_db.query.assert_called_with(Company)
    mock_query.offset.assert_called_with(mock_filter_params.offset)
    mock_offset.limit.assert_called_with(mock_filter_params.limit)
    assert len(result) == 0


def test_getById_returnsCompany_whenCompanyIsFound(
    mocker,
    mock_db,
) -> None:
    # Arrange
    mock_response = mocker.Mock()
    mock_company = mocker.Mock()
    mock_ensure_valid_company_id = mocker.patch(
        "app.services.company_service.ensure_valid_company_id",
        return_value=mock_company,
    )
    mock_create = mocker.patch(
        "app.schemas.company.CompanyResponse.create",
        return_value=mock_response,
    )

    # Act
    result = company_service.get_by_id(id=td.VALID_COMPANY_ID, db=mock_db)

    # Assert
    mock_ensure_valid_company_id.assert_called_with(id=td.VALID_COMPANY_ID, db=mock_db)
    mock_create.assert_called_with(mock_company)
    assert result == mock_response


def test_getByUsername_returnsCompany_whenCompanyIsFound(
    mocker,
    mock_db,
) -> None:
    # Arrange
    mock_company = mocker.Mock(
        id=td.VALID_COMPANY_ID,
        username=td.VALID_COMPANY_USERNAME,
        password=td.VALID_PASSWORD,
    )

    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = mock_company

    # Act
    result = company_service.get_by_username(
        username=td.VALID_COMPANY_USERNAME, db=mock_db
    )

    # Assert
    mock_db.query.assert_called_with(Company)
    assert_filter_called_with(mock_query, Company.username == td.VALID_COMPANY_USERNAME)
    mock_filter.first.assert_called_once()
    assert result.id == td.VALID_COMPANY_ID
    assert result.username == td.VALID_COMPANY_USERNAME
    assert result.password == td.VALID_PASSWORD


def test_getByUsername_raisesApplicationError_whenCompanyIsNotFound(mock_db) -> None:
    # Arrange
    mock_username = td.NON_EXISTENT_USERNAME
    mock_query = mock_db.query.return_value
    mock_query.filter.return_value.first.return_value = None

    # Act & Assert
    with pytest.raises(ApplicationError) as exc:
        company_service.get_by_username(username=mock_username, db=mock_db)

    assert_filter_called_with(mock_query, Company.username == mock_username)
    mock_query.filter.return_value.first.assert_called_once()
    assert exc.value.data.status == status.HTTP_404_NOT_FOUND
    assert exc.value.data.detail == f"Company with username {mock_username} not found"


def test_create_createsCompany_whenDataIsValid(
    mocker,
    mock_db,
) -> None:
    # Arrange
    mock_company_data = mocker.Mock()
    mock_company_data.model_dump.return_value = {}
    mock_city = mocker.Mock(id=td.VALID_CITY_ID)
    mock_response = mocker.Mock()

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
    mock_create = mocker.patch(
        "app.schemas.company.CompanyResponse.create",
        return_value=mock_response,
    )

    # Act
    result = company_service.create(company_data=mock_company_data, db=mock_db)

    # Assert
    mock_ensure_valid_company_creation_data.assert_called_with(
        company_data=mock_company_data, db=mock_db
    )
    mock_ensure_valid_city.assert_called_with(name=mock_company_data.city, db=mock_db)
    mock_hash_password.assert_called_with(mock_company_data.password)
    mock_db.add.assert_called_once_with(ANY)
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(ANY)
    mock_create.assert_called_with(ANY)
    assert result == mock_response


def test_update_updatesCompany_whenDataIsValid(
    mocker,
    mock_db,
) -> None:
    # Arrange
    mock_company_data = mocker.Mock()
    mock_company = mocker.Mock(id=td.VALID_COMPANY_ID)
    mock_response = mocker.Mock()

    mock_ensure_valid_company_id = mocker.patch(
        "app.services.company_service.ensure_valid_company_id",
        return_value=mock_company,
    )
    mock_update_company = mocker.patch(
        "app.services.company_service._update_company",
        return_value=mock_company,
    )
    mock_create = mocker.patch(
        "app.schemas.company.CompanyResponse.create",
        return_value=mock_response,
    )

    # Act
    result = company_service.update(
        id=mock_company.id, company_data=mock_company_data, db=mock_db
    )

    # Assert
    mock_ensure_valid_company_id.assert_called_with(id=td.VALID_COMPANY_ID, db=mock_db)
    mock_update_company.assert_called_with(
        company=mock_company, company_data=mock_company_data, db=mock_db
    )
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(mock_company)
    mock_create.assert_called_with(mock_company)
    assert result == mock_response


def test_uploadLogo_uploadsLogo_whenDataIsValid(
    mocker,
    mock_db,
) -> None:
    # Arrange
    mock_logo = mocker.Mock()
    mock_company = mocker.Mock(id=td.VALID_COMPANY_ID)

    mock_ensure_valid_company_id = mocker.patch(
        "app.services.company_service.ensure_valid_company_id",
        return_value=mock_company,
    )
    mock_handle_file_upload = mocker.patch(
        "app.services.company_service.handle_file_upload",
        return_value=b"mock_logo_data",
    )
    mock_message_response = mocker.patch(
        "app.services.company_service.MessageResponse",
        return_value=mocker.Mock(),
    )

    # Act
    result = company_service.upload_logo(
        company_id=mock_company.id, logo=mock_logo, db=mock_db
    )

    # Assert
    mock_ensure_valid_company_id.assert_called_with(id=mock_company.id, db=mock_db)
    mock_handle_file_upload.assert_called_with(mock_logo)
    mock_db.commit.assert_called_once()
    assert result == mock_message_response.return_value


def test_downloadLogo_returnsLogo_whenCompanyHasLogo(
    mocker,
    mock_db,
) -> None:
    # Arrange
    mock_logo_data = b"mock_logo_data"
    mock_company = mocker.Mock(id=td.VALID_COMPANY_ID, logo=mock_logo_data)

    mock_ensure_valid_company_id = mocker.patch(
        "app.services.company_service.ensure_valid_company_id",
        return_value=mock_company,
    )
    mock_bytes_io = mocker.patch("app.services.company_service.io.BytesIO")
    mock_streaming_response = mocker.patch(
        "app.services.company_service.StreamingResponse"
    )

    # Act
    result = company_service.download_logo(company_id=mock_company.id, db=mock_db)

    # Assert
    mock_ensure_valid_company_id.assert_called_with(id=mock_company.id, db=mock_db)
    mock_bytes_io.assert_called_with(mock_logo_data)
    mock_streaming_response.assert_called_with(
        mock_bytes_io.return_value, media_type="image/png"
    )
    assert result == mock_streaming_response.return_value


def test_downloadLogo_raisesApplicationError_whenCompanyHasNoLogo(
    mocker,
    mock_db,
) -> None:
    # Arrange
    mock_company = mocker.Mock(id=td.VALID_COMPANY_ID, logo=None)

    mock_ensure_valid_company_id = mocker.patch(
        "app.services.company_service.ensure_valid_company_id",
        return_value=mock_company,
    )

    # Act & Assert
    with pytest.raises(ApplicationError) as exc:
        company_service.download_logo(company_id=mock_company.id, db=mock_db)

    mock_ensure_valid_company_id.assert_called_with(id=mock_company.id, db=mock_db)
    assert exc.value.data.status == status.HTTP_404_NOT_FOUND
    assert (
        exc.value.data.detail
        == f"Company with id {mock_company.id} does not have a logo"
    )


def test_updateCompany_updatesName_whenNameIsProvided(
    mocker,
    mock_db,
) -> None:
    # Arrange
    mock_company = mocker.Mock(**td.COMPANY)
    company_update_data = CompanyUpdate(name=td.VALID_COMPANY_NAME_2)

    mock_ensure_valid_city = mocker.patch(
        "app.services.company_service.ensure_valid_city"
    )
    mock_unique_email = mocker.patch(
        "app.services.company_service._ensure_unique_email"
    )
    mock_unique_phone_number = mocker.patch(
        "app.services.company_service._ensure_unique_phone_number"
    )

    # Act
    result = company_service._update_company(
        company=mock_company, company_data=company_update_data, db=mock_db
    )

    # Assert
    mock_ensure_valid_city.assert_not_called()
    mock_unique_email.assert_not_called()
    mock_unique_phone_number.assert_not_called()
    assert result.name == company_update_data.name
    assert isinstance(result.updated_at, datetime)

    assert result.id == mock_company.id
    assert result.description == mock_company.description
    assert result.city == mock_company.city
    assert result.email == mock_company.email
    assert result.phone_number == mock_company.phone_number


def test_updateCompany_updatesDescription_whenDescriptionIsProvided(
    mocker,
    mock_db,
) -> None:
    # Arrange
    mock_company = mocker.Mock(**td.COMPANY)
    company_update_data = CompanyUpdate(description=td.VALID_COMPANY_DESCRIPTION_2)

    mock_ensure_valid_city = mocker.patch(
        "app.services.company_service.ensure_valid_city"
    )
    mock_unique_email = mocker.patch(
        "app.services.company_service._ensure_unique_email"
    )
    mock_unique_phone_number = mocker.patch(
        "app.services.company_service._ensure_unique_phone_number"
    )

    # Act
    result = company_service._update_company(
        company=mock_company, company_data=company_update_data, db=mock_db
    )

    # Assert
    mock_ensure_valid_city.assert_not_called()
    mock_unique_email.assert_not_called()
    mock_unique_phone_number.assert_not_called()
    assert result.description == company_update_data.description
    assert isinstance(result.updated_at, datetime)

    assert result.id == mock_company.id
    assert result.name == mock_company.name
    assert result.city == mock_company.city
    assert result.email == mock_company.email
    assert result.phone_number == mock_company.phone_number


def test_updateCompany_updatesAddressLine_whenAddressLineIsProvided(
    mocker,
    mock_db,
) -> None:
    # Arrange
    mock_company = mocker.Mock(**td.COMPANY)
    company_update_data = CompanyUpdate(address_line=td.VALID_COMPANY_ADDRESS_LINE_2)

    mock_ensure_valid_city = mocker.patch(
        "app.services.company_service.ensure_valid_city"
    )
    mock_unique_email = mocker.patch(
        "app.services.company_service._ensure_unique_email"
    )
    mock_unique_phone_number = mocker.patch(
        "app.services.company_service._ensure_unique_phone_number"
    )

    # Act
    result = company_service._update_company(
        company=mock_company, company_data=company_update_data, db=mock_db
    )

    # Assert
    mock_ensure_valid_city.assert_not_called()
    mock_unique_email.assert_not_called()
    mock_unique_phone_number.assert_not_called()
    assert result.address_line == company_update_data.address_line
    assert isinstance(result.updated_at, datetime)

    assert result.id == mock_company.id
    assert result.name == mock_company.name
    assert result.description == mock_company.description
    assert result.city == mock_company.city
    assert result.email == mock_company.email
    assert result.phone_number == mock_company.phone_number


def test_updateCompany_updatesCity_whenCityIsProvided(
    mocker,
    mock_db,
) -> None:
    # Arrange
    mock_company = mocker.Mock(**td.COMPANY)
    update_company_data = CompanyUpdate(city=td.VALID_CITY_NAME_2)

    mock_city = mocker.Mock(id=td.VALID_CITY_ID_2)
    mock_ensure_valid_city = mocker.patch(
        "app.services.company_service.ensure_valid_city",
        return_value=mock_city,
    )
    mock_unique_email = mocker.patch(
        "app.services.company_service._ensure_unique_email"
    )
    mock_unique_phone_number = mocker.patch(
        "app.services.company_service._ensure_unique_phone_number"
    )

    # Act
    result = company_service._update_company(
        company=mock_company, company_data=update_company_data, db=mock_db
    )

    # Assert
    mock_ensure_valid_city.assert_called_with(name=update_company_data.city, db=mock_db)
    mock_unique_email.assert_not_called()
    mock_unique_phone_number.assert_not_called()
    assert result.city == mock_city
    assert isinstance(result.updated_at, datetime)

    assert result.id == mock_company.id
    assert result.name == mock_company.name
    assert result.description == mock_company.description
    assert result.address_line == mock_company.address_line
    assert result.email == mock_company.email
    assert result.phone_number == mock_company.phone_number


def test_updateCompany_updatesEmail_whenEmailIsProvided(
    mocker,
    mock_db,
) -> None:
    # Arrange
    mock_company = mocker.Mock(**td.COMPANY)
    company_update_data = CompanyUpdate(email=td.VALID_COMPANY_EMAIL_2)

    mock_ensure_valid_city = mocker.patch(
        "app.services.company_service.ensure_valid_city"
    )
    mock_unique_email = mocker.patch(
        "app.services.company_service._ensure_unique_email"
    )
    mock_unique_phone_number = mocker.patch(
        "app.services.company_service._ensure_unique_phone_number"
    )

    # Act
    result = company_service._update_company(
        company=mock_company, company_data=company_update_data, db=mock_db
    )

    # Assert
    mock_ensure_valid_city.assert_not_called()
    mock_unique_email.assert_called_with(email=company_update_data.email, db=mock_db)
    mock_unique_phone_number.assert_not_called()
    assert result.email == company_update_data.email
    assert isinstance(result.updated_at, datetime)

    assert result.id == mock_company.id
    assert result.name == mock_company.name
    assert result.description == mock_company.description
    assert result.address_line == mock_company.address_line
    assert result.city == mock_company.city
    assert result.phone_number == mock_company.phone_number


def test_updateCompany_updatesPhoneNumber_whenPhoneNumberIsProvided(
    mocker,
    mock_db,
) -> None:
    # Arrange
    mock_company = mocker.Mock(**td.COMPANY)
    company_update_data = CompanyUpdate(phone_number=td.VALID_COMPANY_PHONE_NUMBER_2)

    mock_ensure_valid_city = mocker.patch(
        "app.services.company_service.ensure_valid_city"
    )
    mock_unique_email = mocker.patch(
        "app.services.company_service._ensure_unique_email"
    )
    mock_unique_phone_number = mocker.patch(
        "app.services.company_service._ensure_unique_phone_number"
    )

    # Act
    result = company_service._update_company(
        company=mock_company, company_data=company_update_data, db=mock_db
    )

    # Assert
    mock_ensure_valid_city.assert_not_called()
    mock_unique_email.assert_not_called()
    mock_unique_phone_number.assert_called_with(
        phone_number=company_update_data.phone_number, db=mock_db
    )
    assert result.phone_number == company_update_data.phone_number
    assert isinstance(result.updated_at, datetime)

    assert result.id == mock_company.id
    assert result.name == mock_company.name
    assert result.description == mock_company.description
    assert result.address_line == mock_company.address_line
    assert result.city == mock_company.city
    assert result.email == mock_company.email


def test_updateCompany_updatesAllFields_whenAllFieldsAreProvided(
    mocker,
    mock_db,
) -> None:
    # Arrange
    mock_company = mocker.Mock(**td.COMPANY)
    company_update_data = CompanyUpdate(
        name=td.VALID_COMPANY_NAME_2,
        description=td.VALID_COMPANY_DESCRIPTION_2,
        address_line=td.VALID_COMPANY_ADDRESS_LINE_2,
        city=td.VALID_CITY_NAME_2,
        email=td.VALID_COMPANY_EMAIL_2,
        phone_number=td.VALID_COMPANY_PHONE_NUMBER_2,
    )

    mock_city = mocker.Mock(id=td.VALID_CITY_ID_2)
    mock_ensure_valid_city = mocker.patch(
        "app.services.company_service.ensure_valid_city",
        return_value=mock_city,
    )
    mock_unique_email = mocker.patch(
        "app.services.company_service._ensure_unique_email"
    )
    mock_unique_phone_number = mocker.patch(
        "app.services.company_service._ensure_unique_phone_number"
    )

    # Act
    result = company_service._update_company(
        company=mock_company, company_data=company_update_data, db=mock_db
    )

    # Assert
    mock_ensure_valid_city.assert_called_with(name=company_update_data.city, db=mock_db)
    mock_unique_email.assert_called_with(email=company_update_data.email, db=mock_db)
    mock_unique_phone_number.assert_called_with(
        phone_number=company_update_data.phone_number, db=mock_db
    )
    assert result.name == company_update_data.name
    assert result.description == company_update_data.description
    assert result.address_line == company_update_data.address_line
    assert result.city == mock_city
    assert result.email == company_update_data.email
    assert result.phone_number == company_update_data.phone_number
    assert isinstance(result.updated_at, datetime)

    assert result.id == mock_company.id


def test_updateCompany_updatesNothing_whenNoFieldsAreProvided(
    mocker,
    mock_db,
) -> None:
    # Arrange
    mock_company = mocker.Mock(**td.COMPANY)
    company_update_data = CompanyUpdate()

    mock_ensure_valid_city = mocker.patch(
        "app.services.company_service.ensure_valid_city"
    )
    mock_unique_email = mocker.patch(
        "app.services.company_service._ensure_unique_email"
    )
    mock_unique_phone_number = mocker.patch(
        "app.services.company_service._ensure_unique_phone_number"
    )

    # Act
    result = company_service._update_company(
        company=mock_company, company_data=company_update_data, db=mock_db
    )

    # Assert
    mock_ensure_valid_city.assert_not_called()
    mock_unique_email.assert_not_called()
    mock_unique_phone_number.assert_not_called()
    assert result.name == mock_company.name
    assert result.description == mock_company.description
    assert result.address_line == mock_company.address_line
    assert result.city == mock_company.city
    assert result.email == mock_company.email
    assert result.phone_number == mock_company.phone_number
    assert not isinstance(result.updated_at, datetime)

    assert result.id == mock_company.id


def test_ensureUniqueEmail_doesNotRaiseError_whenEmailIsUnique(mock_db) -> None:
    # Arrange
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = None

    # Act
    company_service._ensure_unique_email(email=td.VALID_COMPANY_EMAIL, db=mock_db)

    # Assert
    mock_db.query.assert_called_with(Company)
    assert_filter_called_with(mock_query, Company.email == td.VALID_COMPANY_EMAIL)
    mock_filter.first.assert_called_once()


def test_ensureUniqueEmail_raisesApplicationError_whenEmailIsNotUnique(
    mocker, 
    mock_db
) -> None:
    # Arrange
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = mocker.Mock()

    # Act & Assert
    with pytest.raises(ApplicationError) as exc:
        company_service._ensure_unique_email(email=td.VALID_COMPANY_EMAIL, db=mock_db)

    mock_db.query.assert_called_with(Company)
    assert_filter_called_with(mock_query, Company.email == td.VALID_COMPANY_EMAIL)
    mock_filter.first.assert_called_once()
    assert exc.value.data.status == status.HTTP_409_CONFLICT
    assert exc.value.data.detail == f"Company with email {td.VALID_COMPANY_EMAIL} already exists"


def test_ensureUniquePhoneNumber_doesNotRaiseError_whenPhoneNumberIsUnique(
    mock_db,
) -> None:
    # Arrange
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = None

    # Act
    company_service._ensure_unique_phone_number(
        phone_number=td.VALID_COMPANY_PHONE_NUMBER, db=mock_db
    )

    # Assert
    mock_db.query.assert_called_with(Company)
    assert_filter_called_with(
        mock_query, Company.phone_number == td.VALID_COMPANY_PHONE_NUMBER
    )
    mock_filter.first.assert_called_once()
