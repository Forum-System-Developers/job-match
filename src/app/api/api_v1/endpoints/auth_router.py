from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.schemas.token import AccessToken, Token
from app.schemas.user import UserLogin
from app.services.auth_service import login, refresh_access_token
from app.sql_app.database import get_db
from app.utils.process_request import process_request

router = APIRouter()


@router.post(
    "/login",
    description="Login a user.",
)
def login_user(login_data: UserLogin, db: Session = Depends(get_db)) -> JSONResponse:
    def _login() -> Token:
        return login(login_data=login_data, db=db)

    return process_request(
        get_entities_fn=_login,
        status_code=status.HTTP_200_OK,
        not_found_err_msg="Login failed",
    )


@router.post(
    "/refresh",
    description="Refresh the access token.",
)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)) -> JSONResponse:
    def _refresh() -> AccessToken:
        return refresh_access_token(refresh_token=refresh_token, db=db)

    return process_request(
        get_entities_fn=_refresh,
        status_code=status.HTTP_200_OK,
        not_found_err_msg="Token refresh failed",
    )
