import logging
from datetime import datetime, timedelta

from fastapi import status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from src.app.core.config import get_settings
from src.app.exceptions.custom_exceptions import ApplicationError
from src.app.schemas.token import Token, TokenData
from src.app.sql_app.user.user import User

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


def _create_token_data(user: User) -> TokenData:
    """
    Create token data for a given user.
    Args:
        user (User): The user object for which the token data is to be created.
    Returns:
        TokenData: The token data containing the user's ID as the subject.
    """

    token_data = TokenData(sub=user.id)
    logger.info(f"Created token data for user {user.id}")

    return token_data


def create_access_and_refresh_tokens(user: User) -> Token:
    """
    Create access and refresh tokens for a given user.
    Args:
        user (User): The user for whom the tokens are being created.
    Returns:
        Token: An object containing the access token, refresh token, and token type.
    """

    token_data = _create_token_data(user=user)
    logger.info(f"Created token data for user {user.id}")
    access_token = _create_access_token(token_data)
    logger.info(f"Created access token for user {user.id}")
    refresh_token = _create_refresh_token(token_data)
    logger.info(f"Created refresh token for user {user.id}")

    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )
