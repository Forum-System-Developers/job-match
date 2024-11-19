from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel

from app.sql_app.user.user_type import UserType


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
    Pyantic model representing a User.

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
    Pyantic model representing a user login data.

    Attributes:
        username (str): The username of the User.
        password (str): The password of the User.
        role (UserRole): The role of the User.
    """

    username: str
    password: str
    role: UserRole
