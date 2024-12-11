from fastapi import HTTPException

from app.services.external_db_service_urls import (
    COMPANY_BY_EMAIL_URL,
    COMPANY_BY_PHONE_NUMBER_URL,
    COMPANY_BY_USERNAME_URL,
    JOB_AD_BY_ID_URL,
    JOB_APPLICATIONS_BY_ID_URL,
    MATCH_REQUESTS_BY_ID_URL,
    PROFESSIONAL_BY_EMAIL_URL,
    PROFESSIONAL_BY_USERNAME_URL,
    PROFESSIONALS_BY_ID_URL,
    PROFESSIONALS_BY_SUB_URL,
    SKILLS_URL,
)
from app.services.utils.common import (
    get_company_by_email,
    get_company_by_phone_number,
    get_company_by_username,
    get_job_ad_by_id,
    get_job_application_by_id,
    get_match_request_by_id,
    get_professional_by_email,
    get_professional_by_id,
    get_professional_by_sub,
    get_professional_by_username,
    get_skill_by_id,
)
from tests import test_data as td


def test_getCompanyByUsername_returnsCompany_whenExists(mocker) -> None:
    # Arrange
    username = td.VALID_COMPANY_USERNAME
    mock_company_response = mocker.MagicMock()

    mock_perform_get_request = mocker.patch(
        "app.services.utils.common.perform_get_request",
        return_value=mock_company_response,
    )
    mock_company_response_instance = mocker.patch(
        "app.services.utils.common.CompanyResponse",
        return_value=mock_company_response,
    )

    # Act
    result = get_company_by_username(username=username)

    # Assert
    mock_perform_get_request.assert_called_with(
        url=COMPANY_BY_USERNAME_URL.format(username=username)
    )
    mock_company_response_instance.assert_called_with(**mock_company_response)
    assert result == mock_company_response


def test_get_companyByUsername_returnsNone_whenNotExists(mocker) -> None:
    # Arrange
    username = "invalid_username"
    mock_perform_get_request = mocker.patch(
        "app.services.utils.common.perform_get_request",
        side_effect=HTTPException(status_code=404, detail="Not Found"),
    )

    # Act
    result = get_company_by_username(username=username)

    # Assert
    mock_perform_get_request.assert_called_with(
        url=COMPANY_BY_USERNAME_URL.format(username=username)
    )
    assert result is None


def test_getCompanyByEmail_returnsCompany_whenExists(mocker) -> None:
    # Arrange
    email = td.VALID_COMPANY_EMAIL
    mock_company_response = mocker.MagicMock()

    mock_perform_get_request = mocker.patch(
        "app.services.utils.common.perform_get_request",
        return_value=mock_company_response,
    )
    mock_company_response_instance = mocker.patch(
        "app.services.utils.common.CompanyResponse",
        return_value=mock_company_response,
    )

    # Act
    result = get_company_by_email(email=email)

    # Assert
    mock_perform_get_request.assert_called_with(
        url=COMPANY_BY_EMAIL_URL.format(email=email)
    )
    mock_company_response_instance.assert_called_with(**mock_company_response)
    assert result == mock_company_response


def test_getCompanyByEmail_returnsNone_whenNotExists(mocker) -> None:
    # Arrange
    email = "invalid_email@example.com"
    mock_perform_get_request = mocker.patch(
        "app.services.utils.common.perform_get_request",
        side_effect=HTTPException(status_code=404, detail="Not Found"),
    )

    # Act
    result = get_company_by_email(email=email)

    # Assert
    mock_perform_get_request.assert_called_with(
        url=COMPANY_BY_EMAIL_URL.format(email=email)
    )
    assert result is None


def test_getCompanyByPhoneNumber_returnsCompany_whenExists(mocker) -> None:
    # Arrange
    phone_number = td.VALID_COMPANY_PHONE_NUMBER
    mock_company_response = mocker.MagicMock()

    mock_perform_get_request = mocker.patch(
        "app.services.utils.common.perform_get_request",
        return_value=mock_company_response,
    )
    mock_company_response_instance = mocker.patch(
        "app.services.utils.common.CompanyResponse",
        return_value=mock_company_response,
    )

    # Act
    result = get_company_by_phone_number(phone_number=phone_number)

    # Assert
    mock_perform_get_request.assert_called_with(
        url=COMPANY_BY_PHONE_NUMBER_URL.format(phone_number=phone_number)
    )
    mock_company_response_instance.assert_called_with(**mock_company_response)
    assert result == mock_company_response


def test_getCompanyByPhoneNumber_returnsNone_whenNotExists(mocker) -> None:
    # Arrange
    phone_number = "invalid_phone_number"
    mock_perform_get_request = mocker.patch(
        "app.services.utils.common.perform_get_request",
        side_effect=HTTPException(status_code=404, detail="Not Found"),
    )

    # Act
    result = get_company_by_phone_number(phone_number=phone_number)

    # Assert
    mock_perform_get_request.assert_called_with(
        url=COMPANY_BY_PHONE_NUMBER_URL.format(phone_number=phone_number)
    )
    assert result is None


def test_getProfessionalById_returnsProfessional_whenExists(mocker) -> None:
    # Arrange
    professional_id = td.VALID_PROFESSIONAL_ID
    mock_professional_response = mocker.MagicMock()

    mock_perform_get_request = mocker.patch(
        "app.services.utils.common.perform_get_request",
        return_value=mock_professional_response,
    )
    mock_professional_response_instance = mocker.patch(
        "app.services.utils.common.ProfessionalResponse",
        return_value=mock_professional_response,
    )

    # Act
    result = get_professional_by_id(professional_id=professional_id)

    # Assert
    mock_perform_get_request.assert_called_with(
        url=PROFESSIONALS_BY_ID_URL.format(professional_id=professional_id)
    )
    mock_professional_response_instance.assert_called_with(**mock_professional_response)
    assert result == mock_professional_response


def test_getProfessionalById_returnsNone_whenNotExists(mocker) -> None:
    # Arrange
    professional_id = td.NON_EXISTENT_ID
    mock_perform_get_request = mocker.patch(
        "app.services.utils.common.perform_get_request",
        side_effect=HTTPException(status_code=404, detail="Not Found"),
    )

    # Act
    result = get_professional_by_id(professional_id=professional_id)

    # Assert
    mock_perform_get_request.assert_called_with(
        url=PROFESSIONALS_BY_ID_URL.format(professional_id=professional_id)
    )
    assert result is None


def test_getProfessionalBySub_returnsProfessional_whenExists(mocker) -> None:
    # Arrange
    sub = "test_sub"
    mock_professional_response = mocker.MagicMock()

    mock_perform_get_request = mocker.patch(
        "app.services.utils.common.perform_get_request",
        return_value=mock_professional_response,
    )
    mock_professional_response_instance = mocker.patch(
        "app.services.utils.common.ProfessionalResponse",
        return_value=mock_professional_response,
    )

    # Act
    result = get_professional_by_sub(sub=sub)

    # Assert
    mock_perform_get_request.assert_called_with(
        url=PROFESSIONALS_BY_SUB_URL.format(sub=sub)
    )
    mock_professional_response_instance.assert_called_with(**mock_professional_response)
    assert result == mock_professional_response


def test_getProfessionalBySub_returnsNone_whenNotExists(mocker) -> None:
    # Arrange
    sub = "invalid_sub"
    mock_perform_get_request = mocker.patch(
        "app.services.utils.common.perform_get_request",
        side_effect=HTTPException(status_code=404, detail="Not Found"),
    )

    # Act
    result = get_professional_by_sub(sub=sub)

    # Assert
    mock_perform_get_request.assert_called_with(
        url=PROFESSIONALS_BY_SUB_URL.format(sub=sub)
    )
    assert result is None


def test_getProfessionalByUsername_returnsProfessional_whenExists(mocker) -> None:
    # Arrange
    username = td.VALID_PROFESSIONAL_USERNAME
    mock_professional_response = mocker.MagicMock()

    mock_perform_get_request = mocker.patch(
        "app.services.utils.common.perform_get_request",
        return_value=mock_professional_response,
    )
    mock_professional_response_instance = mocker.patch(
        "app.services.utils.common.ProfessionalResponse",
        return_value=mock_professional_response,
    )

    # Act
    result = get_professional_by_username(username=username)

    # Assert
    mock_perform_get_request.assert_called_with(
        url=PROFESSIONAL_BY_USERNAME_URL.format(username=username)
    )
    mock_professional_response_instance.assert_called_with(**mock_professional_response)
    assert result == mock_professional_response


def test_getProfessionalByUsername_returnsNone_whenNotExists(mocker) -> None:
    # Arrange
    username = "invalid_username"
    mock_perform_get_request = mocker.patch(
        "app.services.utils.common.perform_get_request",
        side_effect=HTTPException(status_code=404, detail="Not Found"),
    )

    # Act
    result = get_professional_by_username(username=username)

    # Assert
    mock_perform_get_request.assert_called_with(
        url=PROFESSIONAL_BY_USERNAME_URL.format(username=username)
    )
    assert result is None


def test_getProfessionalByEmail_returnsProfessional_whenExists(mocker) -> None:
    # Arrange
    email = td.VALID_PROFESSIONAL_EMAIL
    mock_professional_response = mocker.MagicMock()

    mock_perform_get_request = mocker.patch(
        "app.services.utils.common.perform_get_request",
        return_value=mock_professional_response,
    )
    mock_professional_response_instance = mocker.patch(
        "app.services.utils.common.ProfessionalResponse",
        return_value=mock_professional_response,
    )

    # Act
    result = get_professional_by_email(email=email)

    # Assert
    mock_perform_get_request.assert_called_with(
        url=PROFESSIONAL_BY_EMAIL_URL.format(email=email)
    )
    mock_professional_response_instance.assert_called_with(**mock_professional_response)
    assert result == mock_professional_response


def test_getProfessionalByEmail_returnsNone_whenNotExists(mocker) -> None:
    # Arrange
    email = "invalid_email@example.com"
    mock_perform_get_request = mocker.patch(
        "app.services.utils.common.perform_get_request",
        side_effect=HTTPException(status_code=404, detail="Not Found"),
    )

    # Act
    result = get_professional_by_email(email=email)

    # Assert
    mock_perform_get_request.assert_called_with(
        url=PROFESSIONAL_BY_EMAIL_URL.format(email=email)
    )
    assert result is None


def test_getJobApplicationById_returnsJobApplication_whenExists(mocker) -> None:
    # Arrange
    job_application_id = td.VALID_JOB_APPLICATION_ID
    mock_job_application_response = mocker.MagicMock()

    mock_perform_get_request = mocker.patch(
        "app.services.utils.common.perform_get_request",
        return_value=mock_job_application_response,
    )
    mock_job_application_response_instance = mocker.patch(
        "app.services.utils.common.JobApplicationResponse",
        return_value=mock_job_application_response,
    )

    # Act
    result = get_job_application_by_id(job_application_id=job_application_id)

    # Assert
    mock_perform_get_request.assert_called_with(
        url=JOB_APPLICATIONS_BY_ID_URL.format(job_application_id=job_application_id)
    )
    mock_job_application_response_instance.assert_called_with(
        **mock_job_application_response
    )
    assert result == mock_job_application_response


def test_getJobApplicationById_returnsNone_whenNotExists(mocker) -> None:
    # Arrange
    job_application_id = td.NON_EXISTENT_ID
    mock_perform_get_request = mocker.patch(
        "app.services.utils.common.perform_get_request",
        side_effect=HTTPException(status_code=404, detail="Not Found"),
    )

    # Act
    result = get_job_application_by_id(job_application_id=job_application_id)

    # Assert
    mock_perform_get_request.assert_called_with(
        url=JOB_APPLICATIONS_BY_ID_URL.format(job_application_id=job_application_id)
    )
    assert result is None


def test_getJobAdById_returnsJobAd_whenExists(mocker) -> None:
    # Arrange
    job_ad_id = td.VALID_JOB_AD_ID
    mock_job_ad_response = mocker.MagicMock()

    mock_perform_get_request = mocker.patch(
        "app.services.utils.common.perform_get_request",
        return_value=mock_job_ad_response,
    )
    mock_job_ad_response_instance = mocker.patch(
        "app.services.utils.common.JobAdResponse",
        return_value=mock_job_ad_response,
    )

    # Act
    result = get_job_ad_by_id(job_ad_id=job_ad_id)

    # Assert
    mock_perform_get_request.assert_called_with(
        url=JOB_AD_BY_ID_URL.format(job_ad_id=job_ad_id)
    )
    mock_job_ad_response_instance.assert_called_with(**mock_job_ad_response)
    assert result == mock_job_ad_response


def test_getJobAdById_returnsNone_whenNotExists(mocker) -> None:
    # Arrange
    job_ad_id = td.NON_EXISTENT_ID
    mock_perform_get_request = mocker.patch(
        "app.services.utils.common.perform_get_request",
        side_effect=HTTPException(status_code=404, detail="Not Found"),
    )

    # Act
    result = get_job_ad_by_id(job_ad_id=job_ad_id)

    # Assert
    mock_perform_get_request.assert_called_with(
        url=JOB_AD_BY_ID_URL.format(job_ad_id=job_ad_id)
    )
    assert result is None


def test_getMatchRequestById_returnsMatch_whenExists(mocker) -> None:
    # Arrange
    job_ad_id = td.VALID_JOB_AD_ID
    job_application_id = td.VALID_JOB_APPLICATION_ID
    mock_match_response = mocker.MagicMock()

    mock_perform_get_request = mocker.patch(
        "app.services.utils.common.perform_get_request",
        return_value=mock_match_response,
    )
    mock_match_response_instance = mocker.patch(
        "app.services.utils.common.MatchResponse",
        return_value=mock_match_response,
    )

    # Act
    result = get_match_request_by_id(
        job_ad_id=job_ad_id, job_application_id=job_application_id
    )

    # Assert
    mock_perform_get_request.assert_called_with(
        url=MATCH_REQUESTS_BY_ID_URL.format(
            job_ad_id=job_ad_id, job_application_id=job_application_id
        )
    )
    mock_match_response_instance.assert_called_with(**mock_match_response)
    assert result == mock_match_response


def test_getMatchRequestById_returnsNone_whenNotExists(mocker) -> None:
    # Arrange
    job_ad_id = td.NON_EXISTENT_ID
    job_application_id = td.NON_EXISTENT_ID
    mock_perform_get_request = mocker.patch(
        "app.services.utils.common.perform_get_request",
        side_effect=HTTPException(status_code=404, detail="Not Found"),
    )

    # Act
    result = get_match_request_by_id(
        job_ad_id=job_ad_id, job_application_id=job_application_id
    )

    # Assert
    mock_perform_get_request.assert_called_with(
        url=MATCH_REQUESTS_BY_ID_URL.format(
            job_ad_id=job_ad_id, job_application_id=job_application_id
        )
    )
    assert result is None


def test_getSkillById_returnsSkill_whenExists(mocker) -> None:
    # Arrange
    skill_id = td.VALID_SKILL_ID
    mock_skill_response = mocker.MagicMock()

    mock_perform_get_request = mocker.patch(
        "app.services.utils.common.perform_get_request",
        return_value=mock_skill_response,
    )
    mock_skill_response_instance = mocker.patch(
        "app.services.utils.common.SkillResponse",
        return_value=mock_skill_response,
    )

    # Act
    result = get_skill_by_id(skill_id=skill_id)

    # Assert
    mock_perform_get_request.assert_called_with(
        url=SKILLS_URL.format(skill_id=skill_id)
    )
    mock_skill_response_instance.assert_called_with(**mock_skill_response)
    assert result == mock_skill_response


def test_getSkillById_returnsNone_whenNotExists(mocker) -> None:
    # Arrange
    skill_id = td.NON_EXISTENT_ID
    mock_perform_get_request = mocker.patch(
        "app.services.utils.common.perform_get_request",
        side_effect=HTTPException(status_code=404, detail="Not Found"),
    )

    # Act
    result = get_skill_by_id(skill_id=skill_id)

    # Assert
    mock_perform_get_request.assert_called_with(
        url=SKILLS_URL.format(skill_id=skill_id)
    )
    assert result is None
