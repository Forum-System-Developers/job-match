from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.schemas.token import Token
from app.schemas.user import UserResponse
from app.services import auth_service
from app.sql_app.database import get_db

router = APIRouter()


@router.post(
    "/login",
    description="Login a user.",
)
def login_user(
    login_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    response: Response = Response(),
) -> Token:
    return auth_service.login(
        username=login_data.username,
        password=login_data.password,
        db=db,
        response=response,
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
def logout(response: Response) -> Response:
    response = auth_service.logout(response=response)
    response.status_code = status.HTTP_200_OK
    return response


@router.get(
    "/me",
    description="Get the current user.",
)
def get_current_user(
    user: UserResponse = Depends(auth_service.get_current_user),
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"detail": {"role": user.user_role.value}},
    )
