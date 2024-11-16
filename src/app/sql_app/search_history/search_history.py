from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.sql_app.database import Base
from app.sql_app.search_history.history_type import HistoryType

if TYPE_CHECKING:
    from app.sql_app.user.user import User


class SearchHistory(Base):
    """
    Represents a search history model.

    Attributes:
        id (UUID): Unique identifier for the search history record.
        user_id (UUID): Foreign key referencing the user who performed the search.
        type (Enum): Type of the search history.
        parameter (str): Search parameter used by the user.
    Relationships:
        user (relationship): Relationship to the User model.
    """

    __tablename__ = "search_history"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, unique=True, nullable=False
    )
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id"), nullable=False
    )
    type: Mapped[HistoryType] = mapped_column(Enum(HistoryType), nullable=False)
    parameter = mapped_column(String, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="search_history")
