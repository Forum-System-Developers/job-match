import logging
from datetime import datetime, timedelta
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.company import CompanyResponse
from app.schemas.professional import ProfessionalResponse
from app.schemas.token import Token
from app.schemas.user import User, UserLogin, UserResponse, UserRole
from app.services import company_service, professional_service
from app.sql_app.database import get_db
from app.utils.password_utils import verify_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
logger = logging.getLogger(__name__)


def login(username: str, password: str, db: Session, request: Request) -> Token:
    """
    Authenticates a user based on their role and generates access and refresh tokens.

    Args:
        login_data (UserLogin): The login data containing user credentials and role.
        db (Session): The database session for querying user information.
    Returns:
        dict: A dictionary containing the access and refresh tokens.
    """
    login_data = UserLogin(username=username, password=password)
    user_role, user = authenticate_user(login_data=login_data, db=db)
    logger.info(f"Authenticated user {user_role.value} {user.id}")
    token = create_access_and_refresh_tokens(
        user=user, login_data=login_data, user_role=user_role
    )
    logger.info(f"Created tokens for user {user_role.value} {user.id}")

    request.session["user_id"] = str(user.id)
    request.session["user_role"] = user_role.value

    return token


def logout(request: Request) -> dict:
    try:
        request.session.clear()
        return {"message": "Logged out successfully!"}
    except KeyError as e:
        raise ApplicationError(
            detail=f"Exception occurred: {e}, unable to log you out",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def _get_user_role(login_data: UserLogin, db: Session) -> tuple[UserRole, User]:
    user = professional_service.get_by_username(username=login_data.username, db=db)
    if user is not None:
        logger.info(f"Fetched user with user_role {UserRole.PROFESSIONAL.value}")
        return UserRole.PROFESSIONAL, user

    user = company_service.get_by_username(username=login_data.username, db=db)
    if user is not None:
        logger.info(f"Fetched user with user_role {UserRole.COMPANY.value}")
        return UserRole.COMPANY, user


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


def create_access_and_refresh_tokens(
    user: User, login_data: UserLogin, user_role: UserRole
) -> Token:
    """
    Create access and refresh tokens for a given user.

    Args:
        user (User): The user for whom the tokens are being created.
        login_data (UserLogin): The login data containing user role information.
    Returns:
        Token: An object containing the access token, refresh token, and token type.
    """
    token_data = {"sub": str(user.id), "role": str(user_role.value)}
    logger.info(f"Created token data for user {user.id}")
    access_token = _create_access_token(token_data)
    logger.info(f"Created access token for user {user.id}")
    refresh_token = _create_refresh_token(token_data)
    logger.info(f"Created refresh token for user {user.id}")

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


def verify_token(token: str, db: Session) -> tuple[dict, str]:
    """
    Verifies the provided JWT and retrieves the associated user information.

    Args:
        token (str): The JWT token to be verified.
        db (Session): The database session to use for querying user information.
    Returns:
        tuple[dict, str]: The decoded token payload if verification is successful, and the user_role.
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

    user_role = str(payload.get("role"))
    user_id = UUID(payload.get("sub"))
    user_role = _verify_user(user_role=user_role, user_id=user_id, db=db)

    return payload, user_role


def _verify_user(user_role: str, user_id: UUID, db: Session) -> str:
    """
    Verifies user exists.

    Args:
        user_role (str): The user role.
        user_id (UUID): User identifier.
        db (Session): Database dependency

    Raises:
        ApplicationError: If no such user is found.

    Returns:
        UserRole: The role of the current user.
    """
    if user_role == UserRole.COMPANY.value:
        try:
            company_service.get_by_id(id=user_id, db=db)
        except ApplicationError:
            logger.error(f"Company {user_id} not found")
            raise ApplicationError(
                detail="Company not found",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

    elif user_role == UserRole.PROFESSIONAL.value:
        try:
            professional_service.get_by_id(professional_id=user_id, db=db)
        except ApplicationError:
            logger.error(f"Professional {user_id} not found")
            raise ApplicationError(
                detail="Professional not found",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

    return user_role


def authenticate_user(login_data: UserLogin, db: Session) -> tuple[UserRole, User]:
    """
    Authenticates a user based on their role and login credentials.

    Args:
        login_data (UserLogin): The login data containing user credentials.
        db (Session): The database session used to query the user information.
    Returns:
        User: The authenticated user object.
    """
    user_role, user = _get_user_role(login_data=login_data, db=db)

    verified_password: bool = False

    verified_password = verify_password(login_data.password, user.password)
    logger.info(f"Password verified for {user_role.value} {user.id}")

    if not verified_password:
        logger.error("Invalid password")
        raise HTTPException(
            detail="Could not authenticate user",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    return user_role, user


def refresh_access_token(refresh_token: str, db: Session) -> Token:
    """
    Refreshes the access token using the provided refresh token.

    Args:
        refresh_token (str): The refresh token used to verify the user.
        db (Session): The database session used for token verification.
    Returns:
        AccessToken: A new access token for the user.
    """

    payload, user_role = verify_token(token=refresh_token, db=db)
    user_id = payload.get("sub")
    logger.info(f"Verified refresh token for user {user_id}")
    access_token = _create_access_token({"sub": user_id, "role": user_role})
    logger.info(f"Created new access token for user {user_id}")

    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


def get_current_user(
    request: Request, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> UserResponse:
    """
    Retrieve the current user based on the provided token.

    Args:
        token (str): The authentication token provided by the user.
        db (Session): The database session dependency.
    Returns:
        UserResponse: DTO for carrying information about the cirrent logged in user..
    """
    user_id = request.session.get("user_id")
    if user_id is None:
        raise HTTPException(
            detail="Could not authenticate you",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    payload, user_role = verify_token(token=token, db=db)
    user_id = UUID(payload.get("sub"))

    return UserResponse(id=user_id, user_role=UserRole(user_role))


def require_professional_role(
    user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)
) -> ProfessionalResponse:
    user_role = user.user_role
    if user_role != UserRole.PROFESSIONAL:
        raise HTTPException(
            detail="Requires Professional Role", status_code=status.HTTP_403_FORBIDDEN
        )
    professional = professional_service.get_by_id(professional_id=user.id, db=db)
    return professional


def require_company_role(
    user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)
) -> CompanyResponse:
    user_role = user.user_role
    if user_role != UserRole.COMPANY:
        raise HTTPException(
            detail="Requires Company Role", status_code=status.HTTP_403_FORBIDDEN
        )
    company = company_service.get_by_id(id=user.id, db=db)
    return company
