from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.schemas.token import Token
from app.services import auth_service
from app.sql_app.database import get_db
from app.utils.processors import process_request

router = APIRouter()


@router.post(
    "/login",
    description="Login a user.",
)
def login_user(
    request: Request,
    login_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    return auth_service.login(
        username=login_data.username,
        password=login_data.password,
        db=db,
        request=request,
    )


@router.post(
    "/refresh",
    description="Refresh the access token.",
)
def refresh_token(
    refresh_token: str = Depends(auth_service.oauth2_scheme),
    db: Session = Depends(get_db),
) -> Token:
    return auth_service.refresh_access_token(refresh_token=refresh_token, db=db)


@router.post(
    "/logout",
    description="Logs out the current user by invalidating their existing tokens.",
)
def logout(request: Request) -> JSONResponse:
    def _logout():
        return auth_service.logout(request=request)

    return process_request(
        get_entities_fn=_logout,
        status_code=status.HTTP_200_OK,
        not_found_err_msg="Could not log you out",
    )
