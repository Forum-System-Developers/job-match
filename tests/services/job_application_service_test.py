import pytest

from app.schemas.city import City
from app.schemas.job_application import JobApplicationCreate
from app.services import job_application_service
from tests import test_data as td


@pytest.fixture
def mock_db(mocker):
    return mocker.Mock()


def test_create_job_application(mocker, mock_db):
    # Arrange
    skill_1 = mocker.Mock()
    skill_1.id = td.VALID_SKILL_ID
    skill_1.name = td.VALID_SKILL_NAME

    job_application_data = JobApplicationCreate(
        **td.JOB_APPLICATION_CREATE,
        city=td.VALID_CITY_NAME,
        skills=[skill_1],
    )

    mock_professional = mocker.Mock(
        id=td.VALID_PROFESSIONAL_ID,
        active_application_count=td.VALID_PROFESSIONAL_ACTIVE_APPLICATION_COUNT,
    )

    mock_city = mocker.Mock()
    mock_city.id = td.VALID_CITY_ID
    mock_city.name = td.VALID_CITY_NAME

    mock_job_application = mocker.Mock(**td.JOB_APPLICATION)
    mock_job_application.name = td.VALID_JOB_APPLICATION_NAME

    mock_ensure_valid_professional_id = mocker.patch(
        "app.services.job_application_service.ensure_valid_professional_id",
        return_value=mock_professional,
    )

    mock_get_by_name = mocker.patch(
        "app.services.city_service.get_by_name",
        return_value=mock_city,
    )

    mock__create = mocker.patch(
        "app.services.job_application_service._create",
        return_value=mock_job_application,
    )

    mock_JobApplicationResponse = mocker.patch(
        "app.schemas.job_application.JobApplicationResponse.create",
        return_value=mock_job_application,
    )

    mock_create_skillset = mocker.patch(
        "app.services.job_application_service._create_skillset",
        return_value=[],
    )

    # Act

    result = job_application_service.create(
        professional_id=mock_professional.id,
        application_create=job_application_data,
        db=mock_db,
    )

    # Assert
    mock_ensure_valid_professional_id.assert_called_once_with(
        professional_id=mock_professional.id, db=mock_db
    )

    mock_get_by_name.assert_called_once_with(city_name=td.VALID_CITY_NAME, db=mock_db)

    mock__create.assert_called_once_with(
        professional=mock_professional,
        city_id=mock_city.id,
        application_create=job_application_data,
        db=mock_db,
    )

    mock_create_skillset.assert_called_once_with(
        job_application_model=mock_job_application,
        skills=job_application_data.skills,
        db=mock_db,
    )

    assert result == mock_job_application