import pytest
from fastapi import status

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.common import FilterParams
from app.schemas.job_application import JobApplicationCreate, JobApplicationUpdate
from app.services import job_application_service
from app.sql_app.job_application.job_application_status import JobStatus
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


def test_update_job_application(mocker, mock_db):
    # Arrange
    application_update = JobApplicationUpdate(
        **td.JOB_APPLICATION,
        name=td.VALID_JOB_APPLICATION_NAME,
        is_main=True,
        application_status=JobStatus.ACTIVE,
    )

    mock_professional = mocker.Mock(id=td.VALID_PROFESSIONAL_ID)
    mock_job_application = mocker.Mock(id=td.VALID_JOB_APPLICATION_ID)

    mock_get_by_id = mocker.patch(
        "app.services.job_application_service._get_by_id",
        return_value=mock_job_application,
    )

    mock_ensure_valid_professional_id = mocker.patch(
        "app.services.job_application_service.ensure_valid_professional_id",
        return_value=mock_professional,
    )

    mock_update_attributes = mocker.patch(
        "app.services.job_application_service._update_attributes",
        return_value=mock_job_application,
    )

    mock_JobApplicationResponse = mocker.patch(
        "app.schemas.job_application.JobApplicationResponse.create",
        return_value=mock_job_application,
    )

    # Act
    result = job_application_service.update(
        job_application_id=mock_job_application.id,
        professional_id=mock_professional.id,
        application_update=application_update,
        db=mock_db,
    )

    # Assert
    mock_get_by_id.assert_called_once_with(
        job_application_id=mock_job_application.id, db=mock_db
    )

    mock_ensure_valid_professional_id.assert_called_once_with(
        professional_id=mock_professional.id, db=mock_db
    )

    mock_update_attributes.assert_called_once_with(
        application_update=application_update,
        job_application_model=mock_job_application,
        db=mock_db,
    )

    mock_JobApplicationResponse.assert_called_once_with(
        professional=mock_professional,
        job_application=mock_job_application,
        db=mock_db,
    )

    assert result == mock_job_application


def test_get_all_job_applications_withAsc(mocker, mock_db):
    # Arrange
    filter_params = FilterParams(offset=0, limit=10)
    search_params = mocker.Mock(order="asc", order_by="created_at")

    mock_job_app = [(mocker.Mock(), mocker.Mock())]
    mock_job_app_response = [(mocker.Mock(), mocker.Mock())]

    mock_query = mock_db.query.return_value
    mock_join = mock_query.join.return_value
    mock_filter = mock_join.filter.return_value
    mock_offset = mock_filter.offset.return_value
    mock_limit = mock_offset.limit.return_value
    mock_limit.all.return_value = mock_job_app

    mocker.patch(
        "app.schemas.job_application.JobApplicationResponse.create",
        side_effect=mock_job_app_response,
    )

    # Act
    result = job_application_service.get_all(
        filter_params=filter_params,
        search_params=search_params,
        db=mock_db,
    )

    # Assert
    assert result == mock_job_app_response


def test_get_all_job_applications_WithDesc(mocker, mock_db):
    # Arrange
    filter_params = FilterParams(offset=0, limit=10)
    search_params = mocker.Mock(order="desc", order_by="created_at")

    mock_job_app = [(mocker.Mock(), mocker.Mock())]
    mock_job_app_response = [(mocker.Mock(), mocker.Mock())]

    mock_query = mock_db.query.return_value
    mock_join = mock_query.join.return_value
    mock_filter = mock_join.filter.return_value
    mock_offset = mock_filter.offset.return_value
    mock_limit = mock_offset.limit.return_value
    mock_limit.all.return_value = mock_job_app

    mocker.patch(
        "app.schemas.job_application.JobApplicationResponse.create",
        side_effect=mock_job_app_response,
    )

    # Act
    result = job_application_service.get_all(
        filter_params=filter_params,
        search_params=search_params,
        db=mock_db,
    )

    # Assert
    assert result == mock_job_app_response


def test_get_by_id_return_JobApplicationResponse(mocker, mock_db):
    # Arrange
    mock_job_application = mocker.Mock(professional=mocker.Mock())

    mock__get_by_id = mocker.patch(
        "app.services.job_application_service._get_by_id",
        return_value=mock_job_application,
    )

    mock_JobApplicationResponse = mocker.patch(
        "app.schemas.job_application.JobApplicationResponse.create",
        return_value=mock_job_application,
    )

    # Act
    result = job_application_service.get_by_id(
        job_application_id=td.VALID_JOB_APPLICATION_ID,
        db=mock_db,
    )

    # Assert
    mock__get_by_id.assert_called_once_with(
        job_application_id=td.VALID_JOB_APPLICATION_ID, db=mock_db
    )

    mock_JobApplicationResponse.assert_called_once_with(
        professional=mock_job_application.professional,
        job_application=mock_job_application,
        db=mock_db,
    )

    assert result == mock_job_application


def test_get_by_id_return_job_application(mocker, mock_db):
    # Arrange
    mock_job_application = mocker.Mock(id=td.VALID_JOB_APPLICATION_ID)

    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = mock_job_application

    # Act
    result = job_application_service._get_by_id(
        job_application_id=mock_job_application.id,
        db=mock_db,
    )

    # Assert
    assert result == mock_job_application


def test_get_by_id_return_none(mock_db):
    # Arrange
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = None

    # Act
    with pytest.raises(ApplicationError) as exc:
        job_application_service._get_by_id(
            job_application_id=td.VALID_JOB_APPLICATION_ID,
            db=mock_db,
        )

    # Assert
    assert (
        exc.value.data.detail
        == f"Job Aplication with id {td.VALID_JOB_APPLICATION_ID} not found."
    )
    assert exc.value.data.status == status.HTTP_404_NOT_FOUND


def test_update_attributes_updates_min_salary(mocker, mock_db):
    # Arrange
    application_update = mocker.Mock(
        min_salary=50000,
        max_salary=None,
        description=None,
        is_main=None,
        application_status=mocker.Mock(value=JobStatus.ACTIVE),
        city=None,
        skills=None,
    )
    job_application_model = mocker.Mock(
        id=1,
        min_salary=40000,
        max_salary=None,
        description=None,
        is_main=False,
        status=mocker.Mock(value=JobStatus.ACTIVE),
        city=mocker.Mock(name=None),
    )

    mock_db.commit = mocker.Mock()
    mock_db.refresh = mocker.Mock()

    # Act
    result = job_application_service._update_attributes(
        application_update=application_update,
        job_application_model=job_application_model,
        db=mock_db,
    )

    # Assert
    assert result == job_application_model
    assert job_application_model.min_salary == 50000
