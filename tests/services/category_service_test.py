from unittest.mock import call

import pytest

from app.services import category_service
from app.services.external_db_service_urls import CATEGORIES_URL
from tests import test_data as td


def test_getAll_returnsCategories_whenCategoriesExist(mocker):
    # Arrange
    categories = [td.CATEGORY, td.CATEGORY_2]
    mock_perform_get_request = mocker.patch(
        "app.services.category_service.perform_get_request",
        return_value=categories,
    )
    mock_category_response = mocker.patch(
        "app.services.category_service.CategoryResponse",
        return_value=mocker.Mock(),
    )

    # Act
    result = category_service.get_all()

    # Assert
    mock_perform_get_request.assert_called_once_with(url=CATEGORIES_URL)
    mock_category_response.assert_has_calls(
        [call(**categories[0]), call(**categories[1])]
    )
    assert len(result) == 2
    assert isinstance(result, list)


def test_get_all_returns_empty_list_when_no_categories_exist(mocker):
    # Arrange
    mock_perform_get_request = mocker.patch(
        "app.services.category_service.perform_get_request",
        return_value=[],
    )

    # Act
    result = category_service.get_all()

    # Assert
    mock_perform_get_request.assert_called_once_with(url=CATEGORIES_URL)
    assert result == []
