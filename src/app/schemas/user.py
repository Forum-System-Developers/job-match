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
