import logging
from uuid import UUID

from fastapi import status
from sqlalchemy.orm import Session

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.user import UserResponse
from app.sql_app.user.user import User

logger = logging.getLogger(__name__)


def get_by_id(id: UUID, db: Session) -> UserResponse:
    """
    Retrieve a user by their unique identifier.

    Args:
        id (UUID): The unique identifier of the user.
        db (Session): The database session to use for the query.

    Returns:
        UserResponse: The response model containing the user's data.
    """
    user = db.query(User).filter(User.id == id).first()
    if user is None:
        logger.error(f"User with id {id} not found")
        raise ApplicationError(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} not found",
        )
    logger.info(f"Retrieved user with id {id}")

    return UserResponse.model_validate(user)


def get_by_username(username: str, db: Session) -> UserResponse:
    """
    Retrieve a user by their username.

    Args:
        username (str): The username of the user to retrieve.
        db (Session): The database session to use for the query.

    Returns:
        UserResponse: The response model containing the user's data.
    """
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        logger.error(f"User with username {username} not found")
        raise ApplicationError(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with username {username} not found",
        )
    logger.info(f"Retrieved user with username {username}")

    return UserResponse.model_validate(user)
