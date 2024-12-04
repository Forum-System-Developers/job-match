import pytest
from fastapi import status

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.skill import SkillCreate, SkillResponse
from app.services.skill_service import create_pending_skill
from tests import test_data as td


@pytest.fixture
def mock_db(mocker):
    return mocker.Mock()


def test_createPendingSkill_createsSkill_whenValidData(mocker, mock_db):
    # Arrange
    skill_data = SkillCreate(name=td.VALID_SKILL_NAME, category_id=td.VALID_CATEGORY_ID)
    skill_response = (
        SkillResponse(
            id=td.VALID_SKILL_ID,
            name=td.VALID_SKILL_NAME,
            category_id=td.VALID_CATEGORY_ID,
        ),
    )

    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = None

    mock_skill_response = mocker.patch(
        "app.services.skill_service.SkillResponse",
        return_value=skill_response,
    )

    # Act
    response = create_pending_skill(
        company_id=td.VALID_COMPANY_ID, skill_data=skill_data, db=mock_db
    )

    # Assert
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()
    mock_skill_response.assert_called_once()
    assert response == skill_response


def test_createPendingSkill_raisesError_whenSkillAlreadyExists(mocker, mock_db):
    # Arrange
    skill_data = SkillCreate(name=td.VALID_SKILL_NAME, category_id=td.VALID_CATEGORY_ID)

    mock_exists = mocker.patch("app.services.skill_service.exists", return_value=True)

    # Act & Assert
    with pytest.raises(ApplicationError) as exc:
        create_pending_skill(
            company_id=td.VALID_COMPANY_ID, skill_data=skill_data, db=mock_db
        )

    mock_exists.assert_called_with(skill_name=skill_data.name, db=mock_db)
    assert exc.value.data.status == status.HTTP_409_CONFLICT
    assert str(exc.value.data.detail) == f"Skill {skill_data.name} already exists"
