import uuid
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.sql_app.database import Base
from app.sql_app.job_requirement.skill_level import SkillLevel

if TYPE_CHECKING:
    from app.sql_app.job_ad_requirement.job_ads_requirement import JobAdsRequirement


class JobRequirement(Base):
    """
    Represents a job requirement in the database.

    Attributes:
        id (UUID): Unique identifier for the job requirement.
        description (str): Description of the job requirement.
        skill_level (SkillLevel): The skill level required for the job.
        created_at (datetime): Timestamp when the job requirement was created.
        updated_at (datetime): Timestamp when the job requirement was last updated.

    Relationships:
        job_ad_requirements (relationship): Relationship to the JobAdsRequirement model.
    """

    __tablename__ = "job_requirement"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        server_default=func.uuid_generate_v4(),
        primary_key=True,
        unique=True,
        nullable=False,
    )
    description: Mapped[str] = mapped_column(String, nullable=False)
    skill_level: Mapped[SkillLevel] = mapped_column(Enum(SkillLevel), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    job_ad_requirements: Mapped["JobAdsRequirement"] = relationship(
        "JobAdsRequirement",
        back_populates="job_requirement",
        uselist=True,
        collection_class=list,
    )
