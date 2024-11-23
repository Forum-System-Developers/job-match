from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.schemas.token import Token
from app.services.auth_service import login, oauth2_scheme, refresh_access_token
from app.sql_app.database import get_db

router = APIRouter()


@router.post(
    "/login",
    description="Login a user.",
)
def login_user(
    login_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> Token:
    return login(username=login_data.username, password=login_data.password, db=db)


@router.post(
    "/refresh",
    description="Refresh the access token.",
)
def refresh_token(
    refresh_token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> Token:
    return refresh_access_token(refresh_token=refresh_token, db=db)
