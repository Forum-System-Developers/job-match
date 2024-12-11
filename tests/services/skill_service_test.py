import pytest

from app.services.external_db_service_urls import SKILLS_BY_CATEGORY_URL, SKILLS_URL
from app.services.skill_service import create_skill, get_for_category
from tests import test_data as td


def test_createSkill_createsSkillSuccessfully(mocker) -> None:
    # Arrange
    skill_data = mocker.MagicMock()
    skill_response = mocker.MagicMock()

    mock_perform_post_request = mocker.patch(
        "app.services.skill_service.perform_post_request",
        return_value=skill_response,
    )
    mock_skill_response = mocker.patch(
        "app.services.skill_service.SkillResponse",
        return_value=skill_response,
    )

    # Act
    response = create_skill(skill_data=skill_data)

    # Assert
    mock_perform_post_request.assert_called_once_with(
        url=SKILLS_URL,
        json=skill_data.model_dump(mode="json"),
    )
    assert response == skill_response


def test_getForCategory_retrievesSkillsSuccessfully(mocker) -> None:
    # Arrange
    category_id = td.VALID_CATEGORY_ID
    skills_data = [mocker.MagicMock(), mocker.MagicMock()]
    skills_response = [mocker.MagicMock(), mocker.MagicMock()]

    mock_perform_get_request = mocker.patch(
        "app.services.skill_service.perform_get_request",
        return_value=skills_data,
    )
    mock_skill_response = mocker.patch(
        "app.services.skill_service.SkillResponse",
        side_effect=skills_response,
    )

    # Act
    response = get_for_category(category_id=category_id)

    # Assert
    mock_perform_get_request.assert_called_once_with(
        url=SKILLS_BY_CATEGORY_URL.format(category_id=category_id)
    )
    assert response == skills_response
