import logging
from datetime import datetime, timedelta
from uuid import UUID

from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.token import Token, TokenData
from app.schemas.user import UserResponse
from app.services import user_service
from app.sql_app.database import get_db
from app.sql_app.user.user import User
from app.utils.password_utils import verify_password

oauth2_scheme = OAuth2PasswordBearer()
logger = logging.getLogger(__name__)


def _create_access_token(data: dict) -> str:
    """
    Generates an access token for the given user.
    Args:
        data (dict): A dictionary containing user information.
    Returns:
        str: The generated access token as a string.
    """

    access_token = _create_token(
        data=data,
        expires_delta=timedelta(minutes=get_settings().ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    logger.info(f"Generated access token for user {data.get('sub')}")

    return access_token


def _create_refresh_token(data: dict) -> str:
    """
    Generates a refresh token for the given user data.
    Args:
        data (dict): A dictionary containing user information.
    Returns:
        str: The generated refresh token as a string.
    """

    refresh_token = _create_token(
        data=data,
        expires_delta=timedelta(days=get_settings().REFRESH_TOKEN_EXPIRE_DAYS),
    )
    logger.info(f"Generated refresh token for user {data.get('sub')}")

    return refresh_token


def _create_token(data: dict, expires_delta: timedelta) -> str:
    """
    Creates a JSON Web Token (JWT) with the given data and expiration time.
    Args:
        data (dict): The payload data to include in the token.
        expires_delta (timedelta): The time duration after which the token will expire.
    Returns:
        str: The encoded JWT as a string.
    Raises:
        ApplicationError: If the token cannot be created.
    """

    try:
        payload = data.copy()
        expire = datetime.now() + expires_delta
        payload.update({"exp": expire})
        logger.info(f"Creating token with payload: {payload}")
        return jwt.encode(
            payload, get_settings().SECRET_KEY, algorithm=get_settings().ALGORITHM
        )
    except JWTError:
        logger.error(f"Could not create token with payload: {payload}")
        raise ApplicationError(
            detail="Could not create token",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def create_access_and_refresh_tokens(user: User) -> Token:
    """
    Create access and refresh tokens for a given user.
    Args:
        user (User): The user for whom the tokens are being created.
    Returns:
        Token: An object containing the access token, refresh token, and token type.
    """

    token_data = TokenData(sub=str(user.id))
    logger.info(f"Created token data for user {user.id}")
    access_token = _create_access_token(token_data)
    logger.info(f"Created access token for user {user.id}")
    refresh_token = _create_refresh_token(token_data)
    logger.info(f"Created refresh token for user {user.id}")

    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


def verify_token(token: str, db: Session) -> dict:
    """
    Verifies a JWT token and retrieves the associated user from the database.
    Args:
        token (str): The JWT token to be verified.
        db (Session): The database session to use for retrieving the user.
    Returns:
        dict: The decoded payload of the JWT token.
    Raises:
        ApplicationError: If the token cannot be verified or decoded.
    """

    try:
        payload = jwt.decode(
            token, get_settings().SECRET_KEY, algorithms=[get_settings().ALGORITHM]
        )
        logger.info(f"Decoded token payload: {payload}")
    except JWTError:
        logger.error("Could not verify token")
        raise ApplicationError(
            detail="Could not verify token", status_code=status.HTTP_401_UNAUTHORIZED
        )

    user_id = UUID(payload.get("sub"))
    user_service.get_by_id(user_id=user_id, db=db)

    logger.info(f"Retrieved user {user_id}")

    return payload


def authenticate_user(username: str, password: str, db: Session) -> User:
    """
    Authenticate a user by their username and password.
    Args:
        username (str): The username of the user.
        password (str): The password of the user.
        db (Session): The database session to use for querying the user.
    Returns:
        User: The authenticated user object.
    Raises:
        ApplicationError: If the user cannot be authenticated due to invalid credentials.
    """

    user = user_service.get_by_username(username=username, db=db)
    logger.info(f"Retrieved user {user.id} with username {username}")

    verified_password = verify_password(password, user.password)

    if not verified_password:
        logger.error(f"Invalid password for user {user.id}")
        raise ApplicationError(
            detail="Could not authenticate user",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    logger.info(f"Password verified for user {user.id}")

    return user


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> UserResponse:
    """
    Retrieve the current user based on the provided token.
    Args:
        token (str): The authentication token provided by the user.
        db (Session): The database session dependency.
    Returns:
        UserResponse: The user information retrieved from the database.
    Raises:
        ApplicationError: If user not found.
    """

    token_data = verify_token(token=token, db=db)
    user_id = token_data.get("sub")
    user = user_service.get_by_id(user_id=user_id, db=db)
    logger.info(f"Retrieved current user {user_id}")

    return user
