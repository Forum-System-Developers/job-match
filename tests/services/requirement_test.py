from unittest import mock
from uuid import uuid4

import pytest
from fastapi import status
from sqlalchemy.orm import Session

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.requirement import RequirementCreate, RequirementResponse
from app.services.requirement_service import create
from app.sql_app.job_requirement.job_requirement import JobRequirement
from app.sql_app.job_requirement.skill_level import SkillLevel
from tests import test_data as td


@pytest.fixture
def mock_db():
    return mock.Mock(spec=Session)


@pytest.fixture
def requirement_data():
    return RequirementCreate(
        description="Test Requirement",
        skill_level=SkillLevel.INTERMEDIATE,
    )


def test_create_createsRequirement_whenValidData(mocker, mock_db, requirement_data):
    # Arrange
    job_requirement = mocker.Mock(
        id=uuid4(),
        description=requirement_data.description,
        skill_level=requirement_data.skill_level,
        company_id=td.VALID_COMPANY_ID,
    )
    mock_exists = mocker.patch(
        "app.services.requirement_service._exists", return_value=False
    )
    mock_job_requirement = mocker.patch(
        "app.services.requirement_service.JobRequirement", return_value=job_requirement
    )

    # Act
    result = create(
        company_id=td.VALID_COMPANY_ID, requirement_data=requirement_data, db=mock_db
    )

    # Assert
    mock_exists.assert_called_once_with(
        company_id=td.VALID_COMPANY_ID,
        requirement_description=requirement_data.description,
        db=mock_db,
    )
    mock_job_requirement.assert_called_once_with(
        description=requirement_data.description,
        skill_level=requirement_data.skill_level,
        company_id=td.VALID_COMPANY_ID,
    )
    mock_db.add.assert_called_once_with(job_requirement)
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(job_requirement)
    assert isinstance(result, RequirementResponse)
    assert result.description == requirement_data.description
    assert result.skill_level == requirement_data.skill_level
