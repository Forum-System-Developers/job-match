from datetime import timedelta
from uuid import UUID

import pytest
from fastapi import HTTPException, status
from jose import ExpiredSignatureError, JWTError

from app.api.api_v1.endpoints.auth_router import get_current_user
from app.core.config import get_settings
from app.exceptions.custom_exceptions import ApplicationError
from app.main import app
from app.schemas.user import UserRole
from app.services import auth_service
from tests import test_data as td


@pytest.fixture
def override_get_current_user(mocker):
    original_dependency = app.dependency_overrides.get(get_current_user)

    def _override_get_current_user(id, user_role):
        app.dependency_overrides[get_current_user] = mocker.Mock(
            id=id, user_role=user_role
        )

    yield _override_get_current_user

    if original_dependency is not None:
        app.dependency_overrides[get_current_user] = original_dependency
    else:
        del app.dependency_overrides[get_current_user]


def test_login_authenticatesUserSuccessfully(mocker) -> None:
    # Arrange
    username = td.VALID_PROFESSIONAL_USERNAME
    password = td.VALID_PROFESSIONAL_PASSWORD
    response = mocker.Mock()
    user_role = mocker.Mock(value="professional")
    user = mocker.Mock(id="user_id")
    token = mocker.Mock()

    mock_authenticate_user = mocker.patch(
        "app.services.auth_service.authenticate_user",
        return_value=(user_role, user),
    )
    mock_create_access_and_refresh_tokens = mocker.patch(
        "app.services.auth_service.create_access_and_refresh_tokens",
        return_value=token,
    )
    mock_set_cookies = mocker.patch(
        "app.services.auth_service._set_cookies",
        return_value=response,
    )

    # Act
    result = auth_service.login(username=username, password=password, response=response)

    # Assert
    mock_authenticate_user.assert_called_once_with(login_data=mocker.ANY)
    mock_create_access_and_refresh_tokens.assert_called_once_with(
        user=user, login_data=mocker.ANY, user_role=user_role
    )
    mock_set_cookies.assert_called_once_with(response=response, token=token)
    assert result == token


def test_set_cookies_setsCookiesSuccessfully(mocker) -> None:
    # Arrange
    response = mocker.Mock()
    token = mocker.Mock(
        access_token="access_token_value", refresh_token="refresh_token_value"
    )

    # Act
    result = auth_service._set_cookies(response=response, token=token)

    # Assert
    response.set_cookie.assert_any_call(
        key="access_token",
        value="access_token_value",
        httponly=True,
        secure=True,
        samesite="none",
    )
    response.set_cookie.assert_any_call(
        key="refresh_token",
        value="refresh_token_value",
        httponly=True,
        secure=True,
        samesite="none",
    )
    assert result == response


def test_set_cookies_raisesHTTPExceptionOnKeyError(mocker) -> None:
    # Arrange
    response = mocker.Mock()
    token = mocker.Mock(
        access_token="access_token_value", refresh_token="refresh_token_value"
    )
    response.set_cookie.side_effect = KeyError("Test KeyError")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        auth_service._set_cookies(response=response, token=token)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Exception occurred: 'Test KeyError', unable to set cookies" in str(
        exc_info.value.detail
    )


def test_logout_deletesCookiesSuccessfully(mocker) -> None:
    # Arrange
    request = mocker.Mock()
    response = mocker.Mock()
    request.cookies = {
        "access_token": "access_token_value",
        "refresh_token": "refresh_token_value",
    }

    # Act
    result = auth_service.logout(request=request, response=response)

    # Assert
    response.delete_cookie.assert_any_call(
        key="access_token",
        httponly=True,
        secure=True,
        samesite="none",
    )
    response.delete_cookie.assert_any_call(
        key="refresh_token",
        httponly=True,
        secure=True,
        samesite="none",
    )
    assert result == response


def test_logout_deletesOnlyAccessTokenIfNoRefreshToken(mocker) -> None:
    # Arrange
    request = mocker.Mock()
    response = mocker.Mock()
    request.cookies = {"access_token": "access_token_value"}

    # Act
    result = auth_service.logout(request=request, response=response)

    # Assert
    response.delete_cookie.assert_called_once_with(
        key="access_token",
        httponly=True,
        secure=True,
        samesite="none",
    )
    assert result == response


def test_logout_raisesHTTPExceptionOnKeyError(mocker) -> None:
    # Arrange
    request = mocker.Mock()
    response = mocker.Mock()
    request.cookies = {
        "access_token": "access_token_value",
        "refresh_token": "refresh_token_value",
    }
    response.delete_cookie.side_effect = KeyError("Test KeyError")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        auth_service.logout(request=request, response=response)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Exception occurred: 'Test KeyError', unable to log you out" in str(
        exc_info.value.detail
    )


def test_getUserRole_returnsProfessionalRole(mocker) -> None:
    # Arrange
    login_data = mocker.Mock()
    user = mocker.Mock()

    mock_get_by_username = mocker.patch(
        "app.services.professional_service.get_by_username",
        return_value=user,
    )

    # Act
    user_role, result_user = auth_service._get_user_role(login_data=login_data)

    # Assert
    mock_get_by_username.assert_called_once_with(username=login_data.username)
    assert user_role == UserRole.PROFESSIONAL
    assert result_user == user


def test_getUserRole_returnsCompanyRole(mocker) -> None:
    # Arrange
    login_data = mocker.Mock()
    user = mocker.Mock()

    mock_get_by_username = mocker.patch(
        "app.services.company_service.get_by_username",
        return_value=user,
    )
    mock_professional_service_get_by_username = mocker.patch(
        "app.services.professional_service.get_by_username",
        return_value=None,
    )

    # Act
    user_role, result_user = auth_service._get_user_role(login_data=login_data)

    # Assert
    mock_professional_service_get_by_username.assert_called_once_with(
        username=login_data.username
    )
    mock_get_by_username.assert_called_once_with(username=login_data.username)
    assert user_role == UserRole.COMPANY
    assert result_user == user


def test_get_user_role_raisesHTTPExceptionWhenUserNotFound(mocker) -> None:
    # Arrange
    login_data = mocker.Mock()

    mock_professional_service_get_by_username = mocker.patch(
        "app.services.professional_service.get_by_username",
        side_effect=HTTPException(status_code=status.HTTP_404_NOT_FOUND),
    )
    mock_company_service_get_by_username = mocker.patch(
        "app.services.company_service.get_by_username",
        side_effect=HTTPException(status_code=status.HTTP_404_NOT_FOUND),
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc:
        auth_service._get_user_role(login_data=login_data)

    mock_professional_service_get_by_username.assert_called_once_with(
        username=login_data.username
    )
    mock_company_service_get_by_username.assert_called_once_with(
        username=login_data.username
    )
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.value.detail == "Could not authenticate user"


def test_createAccessToken_createsTokenSuccessfully(mocker) -> None:
    # Arrange
    data = {"sub": "user_id", "role": "professional"}
    mock_create_token = mocker.patch(
        "app.services.auth_service._create_token",
        return_value="access_token_value",
    )

    # Act
    access_token = auth_service._create_access_token(data=data)

    # Assert
    mock_create_token.assert_called_once_with(
        data=data,
        expires_delta=timedelta(minutes=get_settings().ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    assert access_token == "access_token_value"


def test_create_refresh_token_createsTokenSuccessfully(mocker) -> None:
    # Arrange
    data = {"sub": "user_id", "role": "professional"}
    mock_create_token = mocker.patch(
        "app.services.auth_service._create_token",
        return_value="refresh_token_value",
    )

    # Act
    refresh_token = auth_service._create_refresh_token(data=data)

    # Assert
    mock_create_token.assert_called_once_with(
        data=data,
        expires_delta=timedelta(days=get_settings().REFRESH_TOKEN_EXPIRE_DAYS),
    )
    assert refresh_token == "refresh_token_value"


def test_createToken_createsTokenSuccessfully(mocker) -> None:
    # Arrange
    data = {"sub": "user_id", "role": "professional"}
    expires_delta = timedelta(minutes=15)
    mock_jwt_encode = mocker.patch(
        "app.services.auth_service.jwt.encode",
        return_value="encoded_token_value",
    )
    mock_get_settings = mocker.patch(
        "app.services.auth_service.get_settings",
        return_value=mocker.Mock(SECRET_KEY="secret_key", ALGORITHM="HS256"),
    )

    # Act
    token = auth_service._create_token(data=data, expires_delta=expires_delta)

    # Assert
    mock_jwt_encode.assert_called_once_with(
        {**data, "exp": mocker.ANY}, "secret_key", algorithm="HS256"
    )
    assert token == "encoded_token_value"


def test_createToken_raisesHTTPExceptionOnJWTError(mocker) -> None:
    # Arrange
    data = {"sub": "user_id", "role": "professional"}
    expires_delta = timedelta(minutes=15)
    mock_jwt_encode = mocker.patch(
        "app.services.auth_service.jwt.encode",
        side_effect=JWTError,
    )
    mock_get_settings = mocker.patch(
        "app.services.auth_service.get_settings",
        return_value=mocker.Mock(SECRET_KEY="secret_key", ALGORITHM="HS256"),
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        auth_service._create_token(data=data, expires_delta=expires_delta)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc_info.value.detail == "Could not create token"


def test_createAccessAndRefreshTokens_createsTokensSuccessfully(mocker) -> None:
    # Arrange
    user = mocker.Mock(id=td.VALID_PROFESSIONAL_ID)
    login_data = mocker.Mock()
    user_role = UserRole.PROFESSIONAL
    token_data = {"sub": str(td.VALID_PROFESSIONAL_ID), "role": "professional"}
    mock_create_access_token = mocker.patch(
        "app.services.auth_service._create_access_token",
        return_value="access_token_value",
    )
    mock_create_refresh_token = mocker.patch(
        "app.services.auth_service._create_refresh_token",
        return_value="refresh_token_value",
    )

    # Act
    token = auth_service.create_access_and_refresh_tokens(
        user=user, login_data=login_data, user_role=user_role
    )

    # Assert
    mock_create_access_token.assert_called_once_with(token_data)
    mock_create_refresh_token.assert_called_once_with(token_data)
    assert token.access_token == "access_token_value"
    assert token.refresh_token == "refresh_token_value"
    assert token.token_type == "bearer"


def test_verifyToken_verifiesTokenSuccessfully(mocker) -> None:
    # Arrange
    token = "valid_token"
    payload = {"sub": str(td.VALID_PROFESSIONAL_ID), "role": "professional"}

    mock_jwt_decode = mocker.patch(
        "app.services.auth_service.jwt.decode",
        return_value=payload,
    )
    mock_get_settings = mocker.patch(
        "app.services.auth_service.get_settings",
        return_value=mocker.Mock(SECRET_KEY="secret_key", ALGORITHM="HS256"),
    )
    mock_verify_user = mocker.patch(
        "app.services.auth_service._verify_user",
        return_value="professional",
    )

    # Act
    result_payload, result_user_role = auth_service.verify_token(token=token)

    # Assert
    mock_jwt_decode.assert_called_once_with(token, "secret_key", algorithms=["HS256"])
    mock_verify_user.assert_called_once_with(
        user_role="professional", user_id=mocker.ANY
    )
    assert result_payload == payload
    assert result_user_role == "professional"


def test_verify_token_raisesHTTPExceptionOnExpiredSignatureError(mocker) -> None:
    # Arrange
    token = "expired_token"

    mock_jwt_decode = mocker.patch(
        "app.services.auth_service.jwt.decode",
        side_effect=ExpiredSignatureError,
    )
    mock_get_settings = mocker.patch(
        "app.services.auth_service.get_settings",
        return_value=mocker.Mock(SECRET_KEY="secret_key", ALGORITHM="HS256"),
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        auth_service.verify_token(token=token)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Token has expired"


def test_verify_token_raisesHTTPExceptionOnJWTError(mocker) -> None:
    # Arrange
    token = "invalid_token"

    mock_jwt_decode = mocker.patch(
        "app.services.auth_service.jwt.decode",
        side_effect=JWTError,
    )
    mock_get_settings = mocker.patch(
        "app.services.auth_service.get_settings",
        return_value=mocker.Mock(SECRET_KEY="secret_key", ALGORITHM="HS256"),
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        auth_service.verify_token(token=token)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Could not verify token"


def test_verifyUser_verifiesCompanySuccessfully(mocker) -> None:
    # Arrange
    user_role = UserRole.COMPANY.value
    user_id = td.VALID_COMPANY_ID
    mock_get_by_id = mocker.patch(
        "app.services.company_service.get_by_id",
        return_value=mocker.Mock(),
    )

    # Act
    result_user_role = auth_service._verify_user(user_role=user_role, user_id=user_id)

    # Assert
    mock_get_by_id.assert_called_once_with(company_id=user_id)
    assert result_user_role == user_role


def test_verify_user_verifiesProfessionalSuccessfully(mocker) -> None:
    # Arrange
    user_role = UserRole.PROFESSIONAL.value
    user_id = td.VALID_PROFESSIONAL_ID
    mock_get_by_id = mocker.patch(
        "app.services.professional_service.get_by_id",
        return_value=mocker.Mock(),
    )

    # Act
    result_user_role = auth_service._verify_user(user_role=user_role, user_id=user_id)

    # Assert
    mock_get_by_id.assert_called_once_with(professional_id=user_id)
    assert result_user_role == user_role


def test_verify_user_raisesHTTPExceptionWhenCompanyNotFound(mocker) -> None:
    # Arrange
    user_role = UserRole.COMPANY.value
    user_id = td.NON_EXISTENT_ID
    mock_get_by_id = mocker.patch(
        "app.services.company_service.get_by_id",
        side_effect=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED),
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        auth_service._verify_user(user_role=user_role, user_id=user_id)

    mock_get_by_id.assert_called_once_with(company_id=user_id)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Company not found"


def test_verify_user_raisesHTTPExceptionWhenProfessionalNotFound(mocker) -> None:
    # Arrange
    user_role = UserRole.PROFESSIONAL.value
    user_id = td.NON_EXISTENT_ID
    mock_get_by_id = mocker.patch(
        "app.services.professional_service.get_by_id",
        side_effect=ApplicationError(detail="Professional not found", status_code=404),
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        auth_service._verify_user(user_role=user_role, user_id=user_id)

    mock_get_by_id.assert_called_once_with(professional_id=user_id)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Professional not found"


def test_authenticateUser_authenticatesSuccessfully(mocker) -> None:
    # Arrange
    login_data = mocker.Mock(
        username=td.VALID_PROFESSIONAL_USERNAME, password=td.VALID_PROFESSIONAL_PASSWORD
    )
    user_role = UserRole.PROFESSIONAL
    user = mocker.Mock(password="hashed_password")

    mock_get_user_role = mocker.patch(
        "app.services.auth_service._get_user_role",
        return_value=(user_role, user),
    )
    mock_verify_password = mocker.patch(
        "app.services.auth_service.verify_password",
        return_value=True,
    )

    # Act
    result_user_role, result_user = auth_service.authenticate_user(
        login_data=login_data
    )

    # Assert
    mock_get_user_role.assert_called_once_with(login_data=login_data)
    mock_verify_password.assert_called_once_with(login_data.password, user.password)
    assert result_user_role == user_role
    assert result_user == user


def test_authenticateUser_raisesHTTPExceptionOnInvalidPassword(mocker) -> None:
    # Arrange
    login_data = mocker.Mock(
        username=td.VALID_PROFESSIONAL_USERNAME, password="invalid_password"
    )
    user_role = UserRole.PROFESSIONAL
    user = mocker.Mock(password="hashed_password")

    mock_get_user_role = mocker.patch(
        "app.services.auth_service._get_user_role",
        return_value=(user_role, user),
    )
    mock_verify_password = mocker.patch(
        "app.services.auth_service.verify_password",
        return_value=False,
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        auth_service.authenticate_user(login_data=login_data)

    mock_get_user_role.assert_called_once_with(login_data=login_data)
    mock_verify_password.assert_called_once_with(login_data.password, user.password)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Could not authenticate user"


def test_refreshAccessToken_refreshesTokenSuccessfully(mocker) -> None:
    # Arrange
    request = mocker.Mock()
    response = mocker.Mock()
    request.cookies = {"refresh_token": "valid_refresh_token"}
    payload = {"sub": str(td.VALID_PROFESSIONAL_ID), "role": "professional"}
    user_role = UserRole.PROFESSIONAL

    mock_verify_token = mocker.patch(
        "app.services.auth_service.verify_token",
        return_value=(payload, user_role.value),
    )
    mock_create_access_token = mocker.patch(
        "app.services.auth_service._create_access_token",
        return_value="new_access_token_value",
    )
    mock_set_cookies = mocker.patch(
        "app.services.auth_service._set_cookies",
        return_value=response,
    )

    # Act
    token = auth_service.refresh_access_token(request=request, response=response)

    # Assert
    mock_verify_token.assert_called_once_with(token="valid_refresh_token")
    mock_create_access_token.assert_called_once_with(
        {"sub": str(td.VALID_PROFESSIONAL_ID), "role": user_role.value}
    )
    mock_set_cookies.assert_called_once_with(response=response, token=mocker.ANY)
    assert token.access_token == "new_access_token_value"
    assert token.refresh_token == "valid_refresh_token"
    assert token.token_type == "bearer"


def test_refreshAccessToken_raisesHTTPExceptionWhenNoRefreshToken(mocker) -> None:
    # Arrange
    request = mocker.Mock()
    response = mocker.Mock()
    request.cookies = {}

    # Act & Assert
    with pytest.raises(HTTPException) as exc:
        auth_service.refresh_access_token(request=request, response=response)

    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.value.detail == "Could not authenticate you"


def test_refreshAccessToken_raisesHTTPExceptionOnInvalidRefreshToken(mocker) -> None:
    # Arrange
    request = mocker.Mock()
    response = mocker.Mock()
    request.cookies = {"refresh_token": "invalid_refresh_token"}

    mock_verify_token = mocker.patch(
        "app.services.auth_service.verify_token",
        side_effect=HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not verify token"
        ),
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc:
        auth_service.refresh_access_token(request=request, response=response)

    mock_verify_token.assert_called_once_with(token="invalid_refresh_token")
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.value.detail == "Could not verify token"


def test_getCurrentUser_returnsUserSuccessfully(mocker) -> None:
    # Arrange
    request = mocker.Mock()
    request.cookies = {"access_token": "valid_access_token"}
    payload = {"sub": str(td.VALID_PROFESSIONAL_ID), "role": "professional"}
    user_role = UserRole.PROFESSIONAL

    mock_verify_token = mocker.patch(
        "app.services.auth_service.verify_token",
        return_value=(payload, user_role.value),
    )

    # Act
    user_response = auth_service.get_current_user(request=request)

    # Assert
    mock_verify_token.assert_called_once_with(token="valid_access_token")
    assert user_response.id == UUID(payload["sub"])
    assert user_response.user_role == user_role


def test_getCurrentUser_raisesHTTPExceptionWhenNoAccessToken(mocker) -> None:
    # Arrange
    request = mocker.Mock()
    request.cookies = {}

    # Act & Assert
    with pytest.raises(HTTPException) as exc:
        auth_service.get_current_user(request=request)

    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.value.detail == "Could not authenticate you"


def test_getCurrentUser_raisesHTTPExceptionOnInvalidAccessToken(mocker) -> None:
    # Arrange
    request = mocker.Mock()
    request.cookies = {"access_token": "invalid_access_token"}

    mock_verify_token = mocker.patch(
        "app.services.auth_service.verify_token",
        side_effect=HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not verify token"
        ),
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc:
        auth_service.get_current_user(request=request)

    mock_verify_token.assert_called_once_with(token="invalid_access_token")
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.value.detail == "Could not verify token"


def test_requireProfessionalRole_returnsProfessionalSuccessfully(
    mocker, override_get_current_user
) -> None:
    # Arrange
    user = mocker.Mock(id=td.VALID_PROFESSIONAL_ID, user_role=UserRole.PROFESSIONAL)
    professional = mocker.Mock()

    override_get_current_user(id=user.id, user_role=user.user_role)

    mock_get_by_id = mocker.patch(
        "app.services.professional_service.get_by_id",
        return_value=professional,
    )

    # Act
    result = auth_service.require_professional_role(user=user)

    # Assert
    mock_get_by_id.assert_called_once_with(professional_id=user.id)
    assert result == professional


def test_requireProfessionalRole_raisesHTTPExceptionWhenUserRoleIsNotProfessional(
    mocker, override_get_current_user
) -> None:
    # Arrange
    user = mocker.Mock(id=td.VALID_COMPANY_ID, user_role=UserRole.COMPANY)

    override_get_current_user(id=user.id, user_role=user.user_role)

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        auth_service.require_professional_role(user=user)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == "Requires Professional Role"


def test_requireProfessionalRole_raisesHTTPExceptionWhenProfessionalNotFound(
    mocker, override_get_current_user
) -> None:
    # Arrange
    user = mocker.Mock(id=td.VALID_PROFESSIONAL_ID, user_role=UserRole.PROFESSIONAL)

    override_get_current_user(id=user.id, user_role=user.user_role)

    mock_get_by_id = mocker.patch(
        "app.services.professional_service.get_by_id",
        side_effect=ApplicationError(
            detail="Professional not found", status_code=status.HTTP_404_NOT_FOUND
        ),
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        auth_service.require_professional_role(user=user)

    mock_get_by_id.assert_called_once_with(professional_id=user.id)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Professional not found"


def test_requireCompanyRole_returnsCompanySuccessfully(
    mocker, override_get_current_user
) -> None:
    # Arrange
    user = mocker.Mock(id=td.VALID_COMPANY_ID, user_role=UserRole.COMPANY)
    company = mocker.Mock()

    override_get_current_user(id=user.id, user_role=user.user_role)

    mock_get_by_id = mocker.patch(
        "app.services.company_service.get_by_id",
        return_value=company,
    )

    # Act
    result = auth_service.require_company_role(user=user)

    # Assert
    mock_get_by_id.assert_called_once_with(company_id=user.id)
    assert result == company


def test_requireCompanyRole_raisesHTTPExceptionWhenUserRoleIsNotCompany(
    mocker, override_get_current_user
) -> None:
    # Arrange
    user = mocker.Mock(id=td.VALID_PROFESSIONAL_ID, user_role=UserRole.PROFESSIONAL)

    override_get_current_user(id=user.id, user_role=user.user_role)

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        auth_service.require_company_role(user=user)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == "Requires Company Role"


def test_requireCompanyRole_raisesHTTPExceptionWhenCompanyNotFound(
    mocker, override_get_current_user
) -> None:
    # Arrange
    user = mocker.Mock(id=td.VALID_COMPANY_ID, user_role=UserRole.COMPANY)

    override_get_current_user(id=user.id, user_role=user.user_role)

    mock_get_by_id = mocker.patch(
        "app.services.company_service.get_by_id",
        side_effect=ApplicationError(
            detail="Company not found", status_code=status.HTTP_404_NOT_FOUND
        ),
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        auth_service.require_company_role(user=user)

    mock_get_by_id.assert_called_once_with(company_id=user.id)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Company not found"


def test_decodeAccessToken_decodesTokenSuccessfully(mocker) -> None:
    # Arrange
    token = "valid_token"
    payload = {"sub": str(td.VALID_PROFESSIONAL_ID), "role": "professional"}

    mock_jwt_decode = mocker.patch(
        "app.services.auth_service.jwt.decode",
        return_value=payload,
    )
    mock_get_settings = mocker.patch(
        "app.services.auth_service.get_settings",
        return_value=mocker.Mock(SECRET_KEY="secret_key", ALGORITHM="HS256"),
    )

    # Act
    result_payload = auth_service.decode_access_token(token=token)

    # Assert
    mock_jwt_decode.assert_called_once_with(token, "secret_key", algorithms=["HS256"])
    assert result_payload == payload
