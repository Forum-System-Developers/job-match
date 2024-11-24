from unittest.mock import ANY

import pytest
from fastapi import status

from app.exceptions.custom_exceptions import ApplicationError
from app.services import company_service
from app.sql_app.company.company import Company
from tests import test_data as td
from tests.utils import assert_filter_called_with


@pytest.fixture
def mock_db(mocker):
    return mocker.Mock()


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
        "app.services.company_service._ensure_valid_city",
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
    mock_ensure_valid_city.assert_called_with(
        city_name=mock_company_data.city, db=mock_db
    )
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
