from datetime import datetime

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.sql_app.database import Base
from app.sql_app.user.user_type import UserType


class User(Base):
    """Represents a user model.

    Attributes:
        id (UUID): The unique identifier for the user, generated automatically.
        username (str): The unique username of the user.
        password (str): The hashed password for the user.
        email (str): The unique email address of the user.
        user_type (UserType): The type of user, as defined by the UserType Enum.
        created_at (datetime): The timestamp when the user was created.
        updated_at (datetime): The timestamp when the user record was last updated.

    Relationships:
        search_history (relationship): The search history associated with the user.
        professional (relationship): Professional profile details of the user, if applicable.
        company (relationship): Company profile details of the user, if applicable.
    """

    __tablename__ = "user"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        server_default=func.uuid_generate_v4(),
        primary_key=True,
        unique=True,
        nullable=False,
    )
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    user_type: Mapped[UserType] = mapped_column(Enum(UserType), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=False,
    )
