import logging
from datetime import datetime, timedelta
from uuid import UUID

from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt

from app.core.config import get_settings
from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.company import CompanyResponse
from app.schemas.professional import ProfessionalResponse
from app.schemas.token import Token
from app.schemas.user import User, UserLogin, UserResponse, UserRole
from app.services import company_service, professional_service
from app.utils.password_utils import verify_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
logger = logging.getLogger(__name__)


def login(username: str, password: str, response: Response) -> Token:
    """
    Authenticates a user based on their role and generates access and refresh tokens.

    Args:
        username (str): The username of the user.
        password (str): The password of the user.
        response (Response): The HTTP response object to set cookies.

    Returns:
        Token: An object containing the access token, refresh token, and token type.
    """
    login_data = UserLogin(username=username, password=password)
    user_role, user = authenticate_user(login_data=login_data)
    logger.info(f"Authenticated user {user_role.value} {user.id}")
    token = create_access_and_refresh_tokens(
        user=user, login_data=login_data, user_role=user_role
    )
    logger.info(f"Created tokens for user {user_role.value} {user.id}")

    response = _set_cookies(response=response, token=token)
    return token


def _set_cookies(response: Response, token: Token) -> Response:
    try:
        response.set_cookie(
            key="access_token",
            value=token.access_token,
            httponly=True,
            secure=True,
            samesite="none",
        )
        response.set_cookie(
            key="refresh_token",
            value=token.refresh_token,
            httponly=True,
            secure=True,
            samesite="none",
        )
        return response
    except KeyError as e:
        raise HTTPException(
            detail=f"Exception occurred: {e}, unable to set cookies",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def logout(request: Request, response: Response) -> Response:
    """
    Logs out the user by deleting the access and refresh tokens from cookies.

    Args:
        response (Response): The HTTP response object to delete cookies.

    Returns:
        Response: The HTTP response object with cookies deleted.
    """
    try:
        response.delete_cookie(
            key="access_token",
            httponly=True,
            secure=True,
            samesite="none",
        )
        if request.cookies.get("refresh_token"):
            response.delete_cookie(
                key="refresh_token",
                httponly=True,
                secure=True,
                samesite="none",
            )

        return response
    except KeyError as e:
        raise HTTPException(
            detail=f"Exception occurred: {e}, unable to log you out",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def _get_user_role(login_data: UserLogin) -> tuple[UserRole, User]:
    """
    Retrieves the user role and user information based on the login data.

    Args:
        login_data (UserLogin): The login data containing username and password.

    Returns:
        tuple[UserRole, User]: A tuple containing the user role and user information.

    Raises:
        HTTPException: If the user cannot be authenticated.
    """
    try:
        user = professional_service.get_by_username(username=login_data.username)
        if user is not None:
            logger.info(f"Fetched user with user_role {UserRole.PROFESSIONAL.value}")
            return UserRole.PROFESSIONAL, user
    except HTTPException:
        pass
    try:
        user = company_service.get_by_username(username=login_data.username)
        if user is not None:
            logger.info(f"Fetched user with user_role {UserRole.COMPANY.value}")
            return UserRole.COMPANY, user
    except HTTPException:
        raise HTTPException(
            detail="Could not authenticate user",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


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
        raise HTTPException(
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
        user_role (UserRole): The role of the user.

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


def verify_token(token: str) -> tuple[dict, str]:
    """
    Verifies the provided JWT and retrieves the associated user information.

    Args:
        token (str): The JWT token to be verified.

    Returns:
        tuple[dict, str]: The decoded token payload if verification is successful, and the user_role.
    """
    try:
        payload = jwt.decode(
            token, get_settings().SECRET_KEY, algorithms=[get_settings().ALGORITHM]
        )
        logger.info(f"Decoded token payload: {payload}")
    except ExpiredSignatureError:
        logger.warning("Token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except JWTError:
        logger.error("Could not verify token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not verify token",
        )

    user_role = str(payload.get("role"))
    user_id = payload.get("sub")
    user_role = _verify_user(user_role=user_role, user_id=UUID(user_id))

    return payload, user_role


def _verify_user(user_role: str, user_id: UUID) -> str:
    """
    Verifies user exists.

    Args:
        user_role (str): The user role.
        user_id (UUID): User identifier.

    Raises:
        HTTPException: If no such user is found.

    Returns:
        UserRole: The role of the current user.
    """
    if user_role == UserRole.COMPANY.value:
        try:
            company_service.get_by_id(company_id=user_id)
        except HTTPException:
            logger.error(f"Company {user_id} not found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Company not found",
            )

    elif user_role == UserRole.PROFESSIONAL.value:
        try:
            professional_service.get_by_id(professional_id=user_id)
        except ApplicationError:
            logger.error(f"Professional {user_id} not found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Professional not found",
            )

    return user_role


def authenticate_user(login_data: UserLogin) -> tuple[UserRole, User]:
    """
    Authenticates a user based on their role and login credentials.

    Args:
        login_data (UserLogin): The login data containing user credentials.

    Returns:
        tuple[UserRole, User]: A tuple containing the user role and the authenticated user object.

    Raises:
        HTTPException: If the user cannot be authenticated.
    """
    user_role, user = _get_user_role(login_data=login_data)

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


def refresh_access_token(request: Request, response: Response) -> Token:
    """
    Refreshes the access token using the provided refresh token.

    Args:
        request (Request): The HTTP request object containing cookies.

    Returns:
        Token: A new access token for the user.
    """
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token is None:
        raise HTTPException(
            detail="Could not authenticate you",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    payload, user_role = verify_token(token=refresh_token)
    user_id = payload.get("sub")
    logger.info(f"Verified refresh token for user {user_id}")
    access_token = _create_access_token({"sub": user_id, "role": user_role})
    logger.info(f"Created new access token for user {user_id}")
    token = Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )
    response = _set_cookies(response=response, token=token)

    return token


def get_current_user(request: Request) -> UserResponse:
    """
    Retrieve the current user based on the provided token.

    Args:
        request (Request): The HTTP request object containing cookies.

    Returns:
        UserResponse: DTO for carrying information about the current logged-in user.

    Raises:
        HTTPException: If the user cannot be authenticated.
    """
    access_token = request.cookies.get("access_token")
    if access_token is None:
        raise HTTPException(
            detail="Could not authenticate you",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    payload, user_role = verify_token(token=access_token)
    user_id = UUID(payload.get("sub"))

    return UserResponse(id=user_id, user_role=UserRole(user_role))


def require_professional_role(
    user: UserResponse = Depends(get_current_user),
) -> ProfessionalResponse:
    """
    Ensures the current user has a professional role.

    Args:
        user (UserResponse): The current user.

    Returns:
        ProfessionalResponse: The professional user information.

    Raises:
        HTTPException: If the user does not have a professional role.
    """
    user_role = user.user_role
    if user_role != UserRole.PROFESSIONAL:
        raise HTTPException(
            detail="Requires Professional Role", status_code=status.HTTP_403_FORBIDDEN
        )
    try:
        professional = professional_service.get_by_id(professional_id=user.id)
    except ApplicationError:
        raise HTTPException(
            detail="Professional not found", status_code=status.HTTP_404_NOT_FOUND
        )
    return professional


def require_company_role(
    user: UserResponse = Depends(get_current_user),
) -> CompanyResponse:
    """
    Ensures the current user has a company role.

    Args:
        user (UserResponse): The current user.

    Returns:
        CompanyResponse: The company user information.

    Raises:
        HTTPException: If the user does not have a company role.
    """
    user_role = user.user_role
    if user_role != UserRole.COMPANY:
        raise HTTPException(
            detail="Requires Company Role", status_code=status.HTTP_403_FORBIDDEN
        )
    try:
        company = company_service.get_by_id(company_id=user.id)
    except ApplicationError:
        raise HTTPException(
            detail="Company not found", status_code=status.HTTP_404_NOT_FOUND
        )
    return company


def decode_access_token(token: str) -> dict:
    """
    Decodes a given JWT access token using the secret key and algorithm specified in the settings.

    Args:
        token (str): The JWT access token to decode.
    Returns:
        dict: The decoded token payload as a dictionary.
    """

    return jwt.decode(
        token, get_settings().SECRET_KEY, algorithms=[get_settings().ALGORITHM]
    )


async def google_get_current_user(request: Request) -> dict:
    """
    Retrieve the current user information from Google using the access token stored in cookies.

    Args:
        request (Request): The incoming HTTP request containing cookies.
    Returns:
        dict: A dictionary containing the user information.
    Raises:
        HTTPException: If the access token is not found in cookies or is invalid.
    """

    access_token = request.cookies.get("access_token")
    if access_token is None:
        raise HTTPException(
            detail="Could not authenticate you",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    user_info = decode_access_token(token=access_token)
    return user_info
