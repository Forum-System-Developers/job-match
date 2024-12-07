import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.services.enums.match_status import MatchStatus
from app.sql_app.database import Base

if TYPE_CHECKING:
    from app.sql_app import JobAd, JobApplication


class Match(Base):
    """
    Represents a match between a job advertisement and a job application.

    Attributes:
        job_ad_id (uuid.UUID): The unique identifier of the job advertisement.
        job_application_id (uuid.UUID): The unique identifier of the job application.
        status (MatchStatus): The status of the match.
        created_at (datetime): The timestamp when the match was created.

    Relationships:
        job_ad (JobAd): The job advertisement associated with this match.
        job_application (JobApplication): The job application associated with this match.
    """

    __tablename__ = "match"

    job_ad_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("job_ad.id"), primary_key=True
    )
    job_application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("job_application.id"), primary_key=True
    )
    status: Mapped[MatchStatus] = mapped_column(Enum(MatchStatus), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    job_ad: Mapped["JobAd"] = relationship("JobAd", back_populates="matches")
    job_application: Mapped["JobApplication"] = relationship(
        "JobApplication", back_populates="matches"
    )
