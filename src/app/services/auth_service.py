import logging
from datetime import datetime, timedelta
from uuid import UUID

from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.company import CompanyResponse
from app.schemas.professional import ProfessionalResponse
from app.schemas.user import User, UserLogin
from app.services import company_service, professional_service
from app.sql_app.database import get_db
from app.utils.password_utils import verify_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="")
logger = logging.getLogger(__name__)


def login(login_data: UserLogin, db: Session) -> dict:
    """
    Authenticates a user based on their role and generates access and refresh tokens.

    Args:
        login_data (UserLogin): The login data containing user credentials and role.
        db (Session): The database session for querying user information.
    Returns:
        dict: A dictionary containing the access and refresh tokens.
    """
    if login_data.role == "company":
        company = authenticate_user(login_data=login_data, db=db)
        logger.info(f"Authenticated company {company.id}")
        token = create_access_and_refresh_tokens(user=company, login_data=login_data)
        logger.info(f"Created tokens for company {company.id}")
    elif login_data.role == "professional":
        professional = authenticate_user(login_data=login_data, db=db)
        logger.info(f"Authenticated professional {professional.id}")
        token = create_access_and_refresh_tokens(
            user=professional, login_data=login_data
        )
        logger.info(f"Created tokens for professional {professional.id}")
    else:
        logger.error(f"Invalid role {login_data.role}")
        raise ApplicationError(
            detail="Invalid role",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return token


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
        str: The generated refresh token.
    """
    refresh_token = _create_token(
        data=data,
        expires_delta=timedelta(days=get_settings().REFRESH_TOKEN_EXPIRE_DAYS),
    )
    logger.info(f"Generated refresh token for user {data.get('sub')}")

    return refresh_token


def _create_token(data: dict, expires_delta: timedelta) -> str:
    """
    Create JWT with the given data.

    Args:
        data (dict): The payload data to include in the token.
        expires_delta (timedelta): The time duration after which the token will expire.

    Returns:
        str: The encoded JWT as a string.
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


def create_access_and_refresh_tokens(user: User, login_data: UserLogin) -> dict:
    """
    Generate access and refresh tokens for a given user.

    Args:
        user (User): The user object containing user details.
        login_data (UserLogin): The login data containing user role information.
    Returns:
        dict: A dictionary containing the access token, refresh token, and token type.
    """
    token_data = {"sub": str(user.id), "role": login_data.role}
    logger.info(f"Created token data for user {user.id}")
    access_token = _create_access_token(token_data)
    logger.info(f"Created access token for user {user.id}")
    refresh_token = _create_refresh_token(token_data)
    logger.info(f"Created refresh token for user {user.id}")

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def verify_token(token: str, db: Session) -> dict:
    """
    Verifies the provided JWT and retrieves the associated user information.

    Args:
        token (str): The JWT token to be verified.
        db (Session): The database session to use for querying user information.
    Returns:
        dict: The decoded token payload if verification is successful.
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

    if payload.get("role") == "company":
        company = company_service.get_by_id(id=UUID(payload.get("sub")), db=db)
        if not company:
            logger.error(f"Company {payload.get('sub')} not found")
            raise ApplicationError(
                detail="Company not found",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
    elif payload.get("role") == "professional":
        professional = professional_service.get_by_id(
            professional_id=UUID(payload.get("sub")), db=db
        )
        if not professional:
            logger.error(f"Professional {payload.get('sub')} not found")
            raise ApplicationError(
                detail="Professional not found",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

    return payload


def authenticate_user(login_data: UserLogin, db: Session) -> User:
    """
    Authenticates a user based on their role and login credentials.

    Args:
        login_data (UserLogin): The login data containing user credentials.
        db (Session): The database session used to query the user information.
    Returns:
        User: The authenticated user object.
    """
    user: User
    verified_password: bool = False

    if login_data.role == "company":
        user = company_service.get_by_username(username=login_data.username, db=db)
        logger.info(f"Retrieved company {user.id}")
        verified_password = verify_password(login_data.password, user.password)
        logger.info(f"Password verified for company {user.id}")
    elif login_data.role == "professional":
        user = professional_service.get_by_username(username=login_data.username, db=db)
        logger.info(f"Retrieved professional {user.id}")
        verified_password = verify_password(login_data.password, user.password)
        logger.info(f"Password verified for professional {user.id}")

    if not verified_password:
        logger.error("Invalid password")
        raise ApplicationError(
            detail="Could not authenticate user",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    return user


def refresh_access_token(refresh_token: str, db: Session) -> str:
    """
    Refreshes the access token using the provided refresh token.

    Args:
        refresh_token (str): The refresh token to be verified and used for generating a new access token.
        db (Session): The database session used for verifying the token.
    Returns:
        str: The newly created access token.
    Raises:
    """
    payload = verify_token(token=refresh_token, db=db)
    user_id = payload.get("sub")
    user_role = payload.get("role")
    logger.info(f"Verified refresh token for user {user_id}")
    access_token = _create_access_token({"sub": user_id, "role": user_role})
    logger.info(f"Created new access token for user {user_id}")

    return access_token


def get_current_company(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> CompanyResponse:
    """
    Retrieve the current company based on the provided token.

    Args:
        token (str): The authentication token provided by the user.
        db (Session): The database session dependency.
    Returns:
        CompanyResponse: The company information associated with the current user.
    """
    token_data = verify_token(token=token, db=db)
    user_id = UUID(token_data.get("sub"))
    company = company_service.get_by_id(id=user_id, db=db)
    logger.info(f"Retrieved current user {user_id}")

    return company


def get_current_professional(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> ProfessionalResponse:
    """
    Retrieve the current professional user based on the provided token.

    Args:
        token (str): The OAuth2 token used for authentication.
        db (Session): The database session dependency.
    Returns:
        ProfessionalResponse: The professional user information.
    """
    token_data = verify_token(token=token, db=db)
    user_id = UUID(token_data.get("sub"))
    professional = professional_service.get_by_id(professional_id=user_id, db=db)
    logger.info(f"Retrieved current user {user_id}")

    return professional
