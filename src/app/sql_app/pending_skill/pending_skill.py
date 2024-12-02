import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.sql_app.database import Base


class PendingSkill(Base):
    """
    Represents a pending skill entity in the database.

    Attributes:
        id (uuid.UUID): Unique identifier for the pending skill.
        category_id (uuid.UUID): Foreign key referencing the category of the skill.
        submitted_by (uuid.UUID): Foreign key referencing the company that submitted the skill.
        name (str): Name of the pending skill.
        created_at (datetime): Timestamp when the pending skill was created.
    """

    __tablename__ = "pending_skill"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        server_default=func.uuid_generate_v4(),
        primary_key=True,
        unique=True,
        nullable=False,
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("category.id"), nullable=False
    )
    submitted_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("company.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
