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
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(job_application_model)


def test_update_attributes_updates_max_salary(mocker, mock_db):
    # Arrange
    application_update = mocker.Mock(
        min_salary=None,
        max_salary=70000,
        description=None,
        is_main=None,
        application_status=mocker.Mock(value=JobStatus.ACTIVE),
        city=None,
        skills=None,
    )
    job_application_model = mocker.Mock(
        id=1,
        min_salary=None,
        max_salary=60000,
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
    assert job_application_model.max_salary == 70000
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(job_application_model)


def test_update_attributes_updates_description(mocker, mock_db):
    # Arrange
    application_update = mocker.Mock(
        min_salary=None,
        max_salary=None,
        description="Updated job description",
        is_main=None,
        application_status=mocker.Mock(value=JobStatus.ACTIVE),
        city=None,
        skills=None,
    )
    job_application_model = mocker.Mock(
        id=1,
        min_salary=None,
        max_salary=None,
        description="Old job description",
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
    assert job_application_model.description == "Updated job description"
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(job_application_model)


def test_update_attributes_updates_is_main(mocker, mock_db):
    # Arrange
    application_update = mocker.Mock(
        min_salary=None,
        max_salary=None,
        description=None,
        is_main=True,
        application_status=mocker.Mock(value=JobStatus.ACTIVE),
        city=None,
        skills=None,
    )
    job_application_model = mocker.Mock(
        id=1,
        min_salary=None,
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
    assert job_application_model.is_main is True
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(job_application_model)


def test_update_attributes_updates_application_status(mocker, mock_db):
    # Arrange
    application_update = mocker.Mock(
        min_salary=None,
        max_salary=None,
        description=None,
        is_main=None,
        application_status=mocker.Mock(value=JobStatus.PRIVATE),
        city=None,
        skills=None,
    )
    job_application_model = mocker.Mock(
        id=1,
        min_salary=None,
        max_salary=None,
        description=None,
        is_main=None,
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
    assert job_application_model.status.value == JobStatus.PRIVATE.value
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(job_application_model)


def test_update_attributes_updates_city(mocker, mock_db):
    # Arrange
    application_update = mocker.Mock(
        min_salary=None,
        max_salary=None,
        description=None,
        is_main=None,
        application_status=mocker.Mock(value=JobStatus.ACTIVE),
        city="New York",
        skills=None,
    )
    job_application_model = mocker.Mock(
        id=1,
        min_salary=None,
        max_salary=None,
        description=None,
        is_main=None,
        status=mocker.Mock(value=JobStatus.ACTIVE),
        city=mocker.Mock(name="Los Angeles"),
    )

    mock_city_response = mocker.Mock(id=td.VALID_CITY_ID)
    mocker.patch(
        "app.services.city_service.get_by_name", return_value=mock_city_response
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
    assert job_application_model.city_id == mock_city_response.id
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(job_application_model)


def test_update_attributes_updates_skills(mocker, mock_db):
    # Arrange
    application_update = mocker.Mock(
        min_salary=None,
        max_salary=None,
        description=None,
        is_main=None,
        application_status=mocker.Mock(value=JobStatus.ACTIVE),
        city=None,
        skills=["Python", "FastAPI"],
    )
    job_application_model = mocker.Mock(
        id=1,
        min_salary=None,
        max_salary=None,
        description=None,
        is_main=None,
        status=mocker.Mock(value=JobStatus.ACTIVE),
        city=mocker.Mock(name="Los Angeles"),
    )

    mock_update_skillset = mocker.patch(
        "app.services.job_application_service._update_skillset"
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
    mock_update_skillset.assert_called_once_with(
        db=mock_db,
        job_application_model=job_application_model,
        skills=["Python", "FastAPI"],
    )
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(job_application_model)


def test_update_skillset_adds_new_skill(mocker, mock_db):
    # Arrange
    skills = [mocker.Mock(name=td.VALID_SKILL_NAME, skill_id=td.VALID_SKILL_ID)]
    job_application_model = mocker.Mock(
        id=td.VALID_JOB_APPLICATION_ID,
        skills=[],
    )

    mock_exists = mocker.patch(
        "app.services.skill_service.exists", side_effect=lambda db, skill_name: False
    )
    mock_create_skill = mocker.patch(
        "app.services.skill_service.create_skill", return_value=skills[0].skill_id
    )
    mock_create_job_application_skill = mocker.patch(
        "app.services.skill_service.create_job_application_skill"
    )

    mock_db.flush = mocker.Mock()

    # Act
    job_application_service._update_skillset(
        db=mock_db,
        job_application_model=job_application_model,
        skills=skills,
    )

    # Assert
    mock_exists.assert_any_call(db=mock_db, skill_name=skills[0].name)
    mock_create_skill.assert_any_call(db=mock_db, skill_data=skills[0])
    mock_create_job_application_skill.assert_any_call(
        db=mock_db,
        skill_id=skills[0].skill_id,
        job_application_id=job_application_model.id,
    )
    mock_db.flush.assert_called_once()


def test_update_skillset_does_not_add_existing_skill(mocker, mock_db):
    # Arrange
    skills = [mocker.Mock(name=td.VALID_SKILL_NAME, skill_id=td.VALID_SKILL_ID)]
    job_application_model = mocker.Mock(
        id=td.VALID_JOB_APPLICATION_ID,
        skills=[],
    )

    mock_exists = mocker.patch(
        "app.services.skill_service.exists", side_effect=lambda db, skill_name: True
    )
    mock_get_id = mocker.patch(
        "app.services.skill_service.get_id", return_value=skills[0].skill_id
    )
    mock_create_job_application_skill = mocker.patch(
        "app.services.skill_service.create_job_application_skill"
    )

    mock_db.flush = mocker.Mock()

    # Act
    job_application_service._update_skillset(
        db=mock_db,
        job_application_model=job_application_model,
        skills=skills,
    )

    # Assert
    mock_exists.assert_any_call(db=mock_db, skill_name=skills[0].name)
    mock_get_id.assert_any_call(db=mock_db, skill_name=skills[0].name)
    mock_create_job_application_skill.assert_any_call(
        db=mock_db,
        skill_id=skills[0].skill_id,
        job_application_id=job_application_model.id,
    )
    mock_db.flush.assert_called_once()
