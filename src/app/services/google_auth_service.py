from fastapi import status
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2AuthorizationCodeBearer
from httpx import AsyncClient

from app.core.config import get_settings
from app.exceptions.custom_exceptions import ApplicationError
from app.services.auth_service import _create_access_token

settings = get_settings()

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://accounts.google.com/o/oauth2/v2/auth",
    tokenUrl="https://oauth2.googleapis.com/token",
)


async def login():
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        "?response_type=code"
        f"&client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={settings.REDIRECT_URI}"
        "&scope=openid%20email%20profile"
    )
    return RedirectResponse(google_auth_url)


async def auth_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        raise ApplicationError(
            detail="Code not found in request query params.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    async with AsyncClient() as client:
        token_response = await client.post(token_url, data=token_data)
        token_response.raise_for_status()
        token_json = token_response.json()

    if "error" in token_json:
        raise ApplicationError(
            detail=token_json["error_description"],
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    access_token = token_json["access_token"]
    user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}

    async with AsyncClient() as client:
        user_info_response = await client.get(user_info_url, headers=headers)
        user_info_response.raise_for_status()
        user_info = user_info_response.json()

    if "error" in user_info:
        raise ApplicationError(
            detail=user_info["error_description"],
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    jwt_token = _create_access_token(data=user_info)
    response = RedirectResponse(url="https://www.rephera.com")
    response.set_cookie(key="access_token", value=jwt_token, httponly=True)

    return response
