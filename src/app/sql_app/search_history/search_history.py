from sqlalchemy import Column, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.app.sql_app.database import Base
from src.app.sql_app.search_history.history_type import HistoryType


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

    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    type = Column(Enum(HistoryType), nullable=False)
    parameter = Column(String, nullable=False)

    user = relationship("User", back_populates="search_history")
