from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.token import Token
from app.schemas.user import UserResponse
from app.services import auth_service

router = APIRouter()


@router.post(
    "/login",
    description="Login a user.",
)
def login_user(
    login_data: OAuth2PasswordRequestForm = Depends(),
    response: Response = Response(),
) -> Token:
    return auth_service.login(
        username=login_data.username,
        password=login_data.password,
        response=response,
    )


@router.post(
    "/refresh",
    description="Refresh the access token.",
)
def refresh_token(
    response: Response,
    request: Request,
) -> Token:
    return auth_service.refresh_access_token(request=request, response=response)


@router.post(
    "/logout",
    description="Logs out the current user by invalidating their existing tokens.",
)
def logout(request: Request, response: Response) -> Response:
    response = auth_service.logout(request=request, response=response)
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
        content={
            "detail": {
                "role": user.user_role.value,
                "id": str(user.id),
            }
        },
    )
