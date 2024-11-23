import uuid

import pytest
from fastapi import status

from app.exceptions.custom_exceptions import ApplicationError
from app.services.utils.validators import (
    ensure_no_match_request,
    ensure_valid_company_id,
    ensure_valid_job_ad_id,
    ensure_valid_job_application_id,
    ensure_valid_location,
    ensure_valid_match_request,
    ensure_valid_professional_id,
    ensure_valid_requirement_id,
    unique_email,
    unique_username,
)
from app.sql_app import (
    City,
    Company,
    JobAd,
    JobApplication,
    JobRequirement,
    Match,
    Professional,
)
from tests.utils import assert_filter_called_with
from tests import test_data as td


@pytest.fixture
def mock_db(mocker):
    return mocker.Mock()


def test_ensureValidLocation_returnsCity_whenLocationIsFound(mocker, mock_db):
    # Arrange
    city = mocker.Mock(name=td.VALID_CITY_NAME)

    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = city

    # Act
    result = ensure_valid_location(location=td.VALID_CITY_NAME, db=mock_db)

    # Assert
    mock_db.query.assert_called_once_with(City)
    assert_filter_called_with(mock_query, City.name == td.VALID_CITY_NAME)
    assert result == city


def test_ensureValidLocation_raisesApplicationError_whenLocationIsNotFound(mock_db):
    # Arrange
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = None

    # Act
    with pytest.raises(ApplicationError) as exc:
        ensure_valid_location(location=td.VALID_CITY_NAME, db=mock_db)

    # Assert
    mock_db.query.assert_called_once_with(City)
    assert_filter_called_with(mock_query, City.name == td.VALID_CITY_NAME)
    assert exc.value.data.status == status.HTTP_404_NOT_FOUND
    assert exc.value.data.detail == f"City with name {td.VALID_CITY_NAME} not found"


def test_ensureValidJobAdId_returnsJobAd_whenJobAdIsFound(mocker, mock_db):
    # Arrange
    job_ad = mocker.Mock(id=td.VALID_JOB_AD_ID)

    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = job_ad

    # Act
    result = ensure_valid_job_ad_id(job_ad_id=td.VALID_JOB_AD_ID, db=mock_db)

    # Assert
    mock_db.query.assert_called_once_with(JobAd)
    assert_filter_called_with(mock_query, JobAd.id == td.VALID_JOB_AD_ID)
    assert result == job_ad


def test_ensureValidJobAdId_returnsJobAd_whenCompanyIsProvided(mocker, mock_db):
    # Arrange
    job_ad = mocker.Mock(id=td.VALID_JOB_AD_ID, company_id=td.VALID_COMPANY_ID)

    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = job_ad

    # Act
    result = ensure_valid_job_ad_id(
        job_ad_id=td.VALID_JOB_AD_ID,
        db=mock_db,
        company_id=td.VALID_COMPANY_ID,
    )

    # Assert
    mock_db.query.assert_called_once_with(JobAd)
    assert_filter_called_with(mock_query, JobAd.id == td.VALID_JOB_AD_ID)
    assert result == job_ad


def test_ensureValidJobAdId_raisesApplicationError_whenJobAdIsNotFound(mock_db):
    # Arrange
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = None

    # Act
    with pytest.raises(ApplicationError) as exc:
        ensure_valid_job_ad_id(job_ad_id=td.NON_EXISTENT_ID, db=mock_db)

    # Assert
    mock_db.query.assert_called_once_with(JobAd)
    assert_filter_called_with(mock_query, JobAd.id == td.NON_EXISTENT_ID)
    assert exc.value.data.status == status.HTTP_404_NOT_FOUND
    assert exc.value.data.detail == f"Job Ad with id {td.NON_EXISTENT_ID} not found"


def test_ensureValidJobAdId_raisesApplicationError_whenJobAdDoesNotBelongToCompany(
    mocker, mock_db
):
    # Arrange
    job_ad = mocker.Mock(id=td.VALID_JOB_AD_ID, company_id=td.NON_EXISTENT_ID)

    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = job_ad

    # Act
    with pytest.raises(ApplicationError) as exc:
        ensure_valid_job_ad_id(
            job_ad_id=td.VALID_JOB_AD_ID, company_id=td.VALID_COMPANY_ID, db=mock_db
        )

    # Assert
    mock_db.query.assert_called_once_with(JobAd)
    assert_filter_called_with(mock_query, JobAd.id == td.VALID_JOB_AD_ID)
    assert exc.value.data.status == status.HTTP_400_BAD_REQUEST
    assert (
        exc.value.data.detail
        == f"Job Ad with id {td.VALID_JOB_AD_ID} does not belong to company with id {td.VALID_COMPANY_ID}"
    )


def test_ensureValidJobApplicationId_returnsJobApplication_whenJobApplicationIsFound(
    mocker, mock_db
):
    # Arrange
    job_application = mocker.Mock(id=td.VALID_JOB_APPLICATION_ID)

    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = job_application

    # Act
    result = ensure_valid_job_application_id(id=td.VALID_JOB_APPLICATION_ID, db=mock_db)

    # Assert
    mock_db.query.assert_called_once_with(JobApplication)
    assert_filter_called_with(mock_query, JobApplication.id == td.VALID_JOB_APPLICATION_ID)
    assert result == job_application


def test_ensureValidJobApplicationId_raisesApplicationError_whenJobApplicationIsNotFound(
    mock_db,
):
    # Arrange
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = None

    # Act
    with pytest.raises(ApplicationError) as exc:
        ensure_valid_job_application_id(id=td.NON_EXISTENT_ID, db=mock_db)

    # Assert
    mock_db.query.assert_called_once_with(JobApplication)
    assert_filter_called_with(mock_query, JobApplication.id == td.NON_EXISTENT_ID)
    assert exc.value.data.status == status.HTTP_404_NOT_FOUND
    assert (
        exc.value.data.detail == f"Job Application with id {td.NON_EXISTENT_ID} not found"
    )


def test_ensureValidCompanyId_returnsCompany_whenCompanyIsFound(mocker, mock_db):
    # Arrange
    company = mocker.Mock(id=td.VALID_COMPANY_ID)

    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = company

    # Act
    result = ensure_valid_company_id(id=td.VALID_COMPANY_ID, db=mock_db)

    # Assert
    mock_db.query.assert_called_once_with(Company)
    assert_filter_called_with(mock_query, Company.id == td.VALID_COMPANY_ID)
    assert result == company


def test_ensureValidCompanyId_raisesApplicationError_whenCompanyIsNotFound(mock_db):
    # Arrange
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = None

    # Act
    with pytest.raises(ApplicationError) as exc:
        ensure_valid_company_id(id=td.NON_EXISTENT_ID, db=mock_db)

    # Assert
    mock_db.query.assert_called_once_with(Company)
    assert_filter_called_with(mock_query, Company.id == td.NON_EXISTENT_ID)
    assert exc.value.data.status == status.HTTP_404_NOT_FOUND
    assert exc.value.data.detail == f"Company with id {td.NON_EXISTENT_ID} not found"


def test_ensureNoMatchRequest_doesNotRaiseApplicationError_whenMatchRequestDoesNotExist(
    mock_db,
):
    # Arrange
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = None

    # Act
    ensure_no_match_request(
        job_ad_id=td.VALID_JOB_AD_ID,
        job_application_id=td.VALID_JOB_APPLICATION_ID,
        db=mock_db,
    )

    # Assert
    mock_db.query.assert_called_once()
    assert_filter_called_with(
        mock_query,
        (Match.job_ad_id == td.VALID_JOB_AD_ID)
        & (Match.job_application_id == td.VALID_JOB_APPLICATION_ID),
    )


def test_ensureNoMatchRequest_raisesApplicationError_whenMatchRequestExists(
    mocker, mock_db
):
    # Arrange
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = mocker.Mock()

    # Act
    with pytest.raises(ApplicationError) as exc:
        ensure_no_match_request(
            job_ad_id=td.VALID_JOB_AD_ID,
            job_application_id=td.VALID_JOB_APPLICATION_ID,
            db=mock_db,
        )

    # Assert
    mock_db.query.assert_called_once()
    assert_filter_called_with(
        mock_query,
        (Match.job_ad_id == td.VALID_JOB_AD_ID)
        & (Match.job_application_id == td.VALID_JOB_APPLICATION_ID),
    )
    assert exc.value.data.status == status.HTTP_400_BAD_REQUEST
    assert (
        exc.value.data.detail
        == f"Match request between job ad with id {td.VALID_JOB_AD_ID} and job application with id {td.VALID_JOB_APPLICATION_ID} already exists"
    )


def test_ensureValidMatchRequest_doesNotRaiseApplicationError_whenMatchRequestIsValid(
    mocker, mock_db
):
    # Arrange
    match_status = mocker.Mock(name="REQUESTED")
    match = mocker.Mock(status=match_status)

    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = match

    # Act
    result = ensure_valid_match_request(
        job_ad_id=td.VALID_JOB_AD_ID,
        job_application_id=td.VALID_JOB_APPLICATION_ID,
        match_status=match_status,
        db=mock_db,
    )

    # Assert
    mock_db.query.assert_called_once()
    assert_filter_called_with(
        mock_query,
        (Match.job_ad_id == td.VALID_JOB_AD_ID)
        & (Match.job_application_id == td.VALID_JOB_APPLICATION_ID),
    )
    assert result == match


def test_ensureValidMatchRequest_raisesApplicationError_whenMatchRequestIsNotFound(
    mocker, mock_db
):
    # Arrange
    match_status = mocker.Mock(name="REQUESTED")
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = None

    # Act
    with pytest.raises(ApplicationError) as exc:
        ensure_valid_match_request(
            job_ad_id=td.VALID_JOB_AD_ID,
            job_application_id=td.VALID_JOB_APPLICATION_ID,
            match_status=match_status,
            db=mock_db,
        )

    # Assert
    mock_db.query.assert_called_once()
    assert_filter_called_with(
        mock_query,
        (Match.job_ad_id == td.VALID_JOB_AD_ID)
        & (Match.job_application_id == td.VALID_JOB_APPLICATION_ID),
    )
    assert exc.value.data.status == status.HTTP_404_NOT_FOUND
    assert (
        exc.value.data.detail
        == f"Match request with job ad id {td.VALID_JOB_AD_ID} and job application id {td.VALID_JOB_APPLICATION_ID} not found"
    )


def test_ensureValidMatchRequest_raisesApplicationError_whenMatchRequestIsNotInRequestedStatus(
    mocker, mock_db
):
    # Arrange
    match_status = mocker.Mock(name="REQUESTED")
    match = mocker.Mock(status="ACCEPTED")

    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = match

    # Act
    with pytest.raises(ApplicationError) as exc:
        ensure_valid_match_request(
            job_ad_id=td.VALID_JOB_AD_ID,
            job_application_id=td.VALID_JOB_APPLICATION_ID,
            match_status=match_status,
            db=mock_db,
        )

    # Assert
    mock_db.query.assert_called_once_with(Match)
    assert_filter_called_with(
        mock_query,
        (Match.job_ad_id == td.VALID_JOB_AD_ID)
        & (Match.job_application_id == td.VALID_JOB_APPLICATION_ID),
    )
    assert exc.value.data.status == status.HTTP_400_BAD_REQUEST
    assert (
        exc.value.data.detail
        == f"Match request with job ad id {td.VALID_JOB_AD_ID} and job application id {td.VALID_JOB_APPLICATION_ID} is not in {match_status.name} status"
    )


def test_ensureValidRequirementId_returnsRequirement_whenRequirementIsFound(
    mocker, mock_db
):
    # Arrange
    requirement = mocker.Mock(id=td.VALID_REQUIREMENT_ID, company_id=td.VALID_COMPANY_ID)

    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = requirement

    # Act
    result = ensure_valid_requirement_id(
        requirement_id=requirement.id, company_id=td.VALID_COMPANY_ID, db=mock_db
    )

    # Assert
    mock_db.query.assert_called_once_with(JobRequirement)
    assert_filter_called_with(
        mock_query,
        (JobRequirement.id == td.VALID_REQUIREMENT_ID)
        & (JobRequirement.company_id == td.VALID_COMPANY_ID),
    )
    assert result == requirement


def test_ensureValidRequirementId_raisesApplicationError_whenRequirementIsNotFound(
    mock_db,
):
    # Arrange
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = None

    # Act
    with pytest.raises(ApplicationError) as exc:
        ensure_valid_requirement_id(
            requirement_id=td.VALID_REQUIREMENT_ID, company_id=td.VALID_COMPANY_ID, db=mock_db
        )

    # Assert
    mock_db.query.assert_called_once_with(JobRequirement)
    assert_filter_called_with(
        mock_query,
        (JobRequirement.id == td.VALID_REQUIREMENT_ID)
        & (JobRequirement.company_id == td.VALID_COMPANY_ID),
    )
    assert exc.value.data.status == status.HTTP_404_NOT_FOUND
    assert (
        exc.value.data.detail == f"Requirement with id {td.VALID_REQUIREMENT_ID} not found"
    )


def test_uniqueUsername_returnsTrue_whenUsernameIsUnique(mock_db):
    # Arrange
    username = "unique_username"
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.side_effect = [None, None]

    # Act
    result = unique_username(username=username, db=mock_db)

    # Assert
    mock_db.query.assert_any_call(Professional.username)
    mock_db.query.assert_any_call(Company.username)
    assert result is True


def test_uniqueUsername_returnsFalse_whenUsernameExistsInProfessional(mocker, mock_db):
    # Arrange
    username = "existing_username"
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.side_effect = [mocker.Mock(), None]

    # Act
    result = unique_username(username=username, db=mock_db)

    # Assert
    mock_db.query.assert_called_once_with(Professional.username)
    assert result is False


def test_uniqueUsername_returnsFalse_whenUsernameExistsInCompany(mocker, mock_db):
    # Arrange
    username = "existing_username"
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.side_effect = [None, mocker.Mock()]

    # Act
    result = unique_username(username=username, db=mock_db)

    # Assert
    mock_db.query.assert_any_call(Professional.username)
    mock_db.query.assert_any_call(Company.username)
    assert result is False


def test_uniqueEmail_returnsTrue_whenEmailIsUnique(mock_db):
    # Arrange
    email = "unique_email"
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.side_effect = [None, None]

    # Act
    result = unique_email(email=email, db=mock_db)

    # Assert
    mock_db.query.assert_any_call(Professional.email)
    mock_db.query.assert_any_call(Company.email)
    assert result is True


def test_uniqueEmail_returnsFalse_whenEmailExistsInProfessional(mocker, mock_db):
    # Arrange
    email = "existing_email"
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.side_effect = [mocker.Mock(), None]

    # Act
    result = unique_email(email=email, db=mock_db)

    # Assert
    mock_db.query.assert_called_once_with(Professional.email)
    assert result is False


def test_uniqueEmail_returnsFalse_whenEmailExistsInCompany(mocker, mock_db):
    # Arrange
    email = "existing_email"
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.side_effect = [None, mocker.Mock()]

    # Act
    result = unique_email(email=email, db=mock_db)

    # Assert
    mock_db.query.assert_any_call(Professional.email)
    mock_db.query.assert_any_call(Company.email)
    assert result is False


def test_ensureValidProfessionalId_returnsProfessional_whenProfessionalIsFound(
    mocker, mock_db
):
    # Arrange
    professional = mocker.Mock(id=uuid.uuid4())

    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = professional

    # Act
    result = ensure_valid_professional_id(professional_id=professional.id, db=mock_db)

    # Assert
    mock_db.query.assert_called_once_with(Professional)
    assert_filter_called_with(mock_query, Professional.id == professional.id)
    assert result == professional
