from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.sql_app.user.user_type import UserType


class BaseUser(BaseModel):
    id: UUID
    username: str
    email: str
    user_type: UserType
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserResponse(BaseUser):
    password: str


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
