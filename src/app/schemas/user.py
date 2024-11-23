from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class UserRole(Enum):
    """
    Representing the different roles a user can have.

    Attributes:
        COMPANY (str): Represents a company user role.
        PROFESSIONAL (str): Represents a professional user role.
    """

    COMPANY = "company"
    PROFESSIONAL = "professional"


class User(BaseModel):
    """
    Pydantic model representing a User.

    Attributes:
        id (UUID): The identifier of the User.
        username (str): The username of the User.
        password (str): The password of the User.
    """

    id: UUID
    username: str
    password: str


class UserLogin(BaseModel):
    """
    Pydantic model representing user login data.

    Attributes:
        username (str): The username of the User.
        password (str): The password of the User.
    """

    username: str
    password: str


class UserResponse(BaseModel):
    """
    Pydantic model representing UserResponse.

    Attributes:
        id (UUID): The identifier of the User.
        role (UserRole): The role of the User.
    """

    id: UUID
    user_role: UserRole
