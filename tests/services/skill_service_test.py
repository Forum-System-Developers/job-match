import pytest
from fastapi import status

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.skill import SkillCreate, SkillResponse
from app.services.skill_service import (
    create_job_application_skill,
    create_pending_skill,
    create_skill,
    exists,
)
from app.sql_app.skill.skill import Skill
from tests import test_data as td
from tests.utils import assert_filter_called_with


@pytest.fixture
def mock_db(mocker):
    return mocker.Mock()


def test_createSkill_createsSkill_whenValidData(mocker, mock_db):
    # Arrange
    skill_data = SkillCreate(name=td.VALID_SKILL_NAME, category_id=td.VALID_CATEGORY_ID)
    skill_id = td.VALID_SKILL_ID

    mock_skill = mocker.patch("app.services.skill_service.Skill")
    mock_skill_instance = mock_skill.return_value
    mock_skill_instance.id = skill_id

    # Act
    response = create_skill(db=mock_db, skill_data=skill_data)

    # Assert
    mock_db.add.assert_called_once_with(mock_skill_instance)
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(mock_skill_instance)
    assert response == skill_id


def test_createJobApplicationSkill_createsJobApplicationSkill_whenValidData(
    mocker, mock_db
):
    # Arrange
    skill_id = td.VALID_SKILL_ID
    job_application_id = td.VALID_JOB_APPLICATION_ID

    mock_job_application_skill = mocker.patch(
        "app.services.skill_service.JobApplicationSkill"
    )
    mock_job_application_skill_instance = mock_job_application_skill.return_value

    # Act
    response = create_job_application_skill(
        db=mock_db, skill_id=skill_id, job_application_id=job_application_id
    )

    # Assert
    mock_db.add.assert_called_once_with(mock_job_application_skill_instance)
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(mock_job_application_skill_instance)
    assert response == skill_id


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


def test_exists_returnsTrue_whenSkillExists(mocker, mock_db):
    # Arrange
    skill_name = td.VALID_SKILL_NAME
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = True

    # Act
    result = exists(db=mock_db, skill_name=skill_name)

    # Assert
    mock_db.query.assert_called_once_with(Skill)
    assert_filter_called_with(mock_query, Skill.name == skill_name)
    mock_filter.first.assert_called_once()
    assert result is True


def test_exists_returnsFalse_whenSkillDoesNotExist(mocker, mock_db):
    # Arrange
    skill_name = td.VALID_SKILL_NAME
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = None

    # Act
    result = exists(db=mock_db, skill_name=skill_name)

    # Assert
    mock_db.query.assert_called_once_with(Skill)
    assert_filter_called_with(mock_query, Skill.name == skill_name)
    mock_filter.first.assert_called_once()
    assert result is False
