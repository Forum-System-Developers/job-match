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
