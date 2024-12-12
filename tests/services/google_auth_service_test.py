import pytest
from fastapi import status
from fastapi.responses import RedirectResponse

from app.exceptions.custom_exceptions import ApplicationError
from app.services.google_auth_service import (
    _create_token_payload_from_user_info,
    auth_callback,
    login,
)
from tests import test_data as td


@pytest.mark.asyncio
async def test_login_redirect():
    response = await login()
    assert isinstance(response, RedirectResponse)
    assert (
        "https://accounts.google.com/o/oauth2/v2/auth" in response.headers["location"]
    )
    assert "client_id=" in response.headers["location"]
    assert "redirect_uri=" in response.headers["location"]
    assert "scope=" in response.headers["location"]


@pytest.mark.asyncio
async def test_auth_callback_success(mocker):
    professional = mocker.Mock()
    professional.id = td.VALID_PROFESSIONAL_ID

    request = mocker.Mock()
    request.query_params.get = mocker.Mock(return_value="test_code")

    mock_google_token_response = {
        "access_token": "test_access_token",
        "expires_in": 3600,
        "token_type": "Bearer",
    }
    mocker.patch(
        "app.services.google_auth_service.AsyncClient.post",
        return_value=mocker.Mock(
            json=mocker.Mock(return_value=mock_google_token_response),
            raise_for_status=mocker.Mock(return_value=None),
        ),
    )

    mock_google_user_info = {
        "email": "test@example.com",
        "name": "Test User",
        "sub": "test_sub_id",
    }
    mocker.patch(
        "app.services.google_auth_service.AsyncClient.get",
        return_value=mocker.Mock(
            json=mocker.Mock(return_value=mock_google_user_info),
            raise_for_status=mocker.Mock(return_value=None),
        ),
    )

    mock_jwt_token = "mock_jwt_token"
    mocker.patch(
        "app.services.google_auth_service._create_access_token",
        return_value=mock_jwt_token,
    )

    mocker.patch(
        "app.services.professional_service.get_or_create_from_google_token",
        return_value=professional,
    )

    response = await auth_callback(request)

    assert isinstance(response, RedirectResponse)
    assert response.headers["location"] == "https://www.rephera.com"

    assert response.headers["set-cookie"].startswith("access_token=mock_jwt_token")


@pytest.mark.asyncio
async def test_auth_callback_missing_code(mocker):
    request = mocker.Mock()
    request.query_params.get = mocker.Mock(return_value=None)

    with pytest.raises(ApplicationError) as exc:
        await auth_callback(request)

    assert exc.value.data.status == status.HTTP_400_BAD_REQUEST
    assert exc.value.data.detail == "Code not found in request query params."


@pytest.mark.asyncio
async def test_auth_callback_google_error(mocker):
    request = mocker.Mock()
    request.query_params.get = mocker.Mock(return_value="test_code")

    mock_google_error_response = {
        "error": "invalid_grant",
        "error_description": "Invalid code.",
    }
    mocker.patch(
        "app.services.google_auth_service.AsyncClient.post",
        return_value=mocker.Mock(
            json=mocker.Mock(return_value=mock_google_error_response),
            raise_for_status=mocker.Mock(side_effect="error"),
        ),
    )

    with pytest.raises(ApplicationError) as exc:
        await auth_callback(request)

    assert exc.value.data.status == status.HTTP_400_BAD_REQUEST
    assert exc.value.data.detail == "Invalid code."


@pytest.mark.asyncio
async def test_auth_callback_google_user_info_error(mocker):
    request = mocker.Mock()
    request.query_params.get = mocker.Mock(return_value="test_code")

    mock_user_info_error = {
        "error": "some_error",
        "error_description": "Something went wrong",
    }

    mocker.patch(
        "app.services.google_auth_service.AsyncClient.post",
        return_value=mocker.Mock(
            json=mocker.Mock(return_value={"access_token": "some_token"}),
            raise_for_status=mocker.Mock(side_effect=None),
        ),
    )

    mocker.patch(
        "app.services.google_auth_service.AsyncClient.get",
        return_value=mocker.Mock(
            json=mocker.Mock(return_value=mock_user_info_error),
            raise_for_status=mocker.Mock(side_effect=None),
        ),
    )

    with pytest.raises(ApplicationError) as exc:
        await auth_callback(request)

    assert exc.value.data.status == status.HTTP_400_BAD_REQUEST
    assert exc.value.data.detail == "Something went wrong"


def test_create_token_payload_from_user_info(mocker):
    # Arrange
    user_info = {}

    professional = mocker.Mock()
    professional.id = td.VALID_PROFESSIONAL_ID

    mock_professional_service = mocker.patch(
        "app.services.professional_service.get_or_create_from_google_token",
        return_value=professional,
    )

    # Act
    result = _create_token_payload_from_user_info(user_info=user_info)

    # Assert
    assert result["sub"] == str(td.VALID_PROFESSIONAL_ID)
