import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.sql_app.database import Base


class JobAdSkill(Base):
    """
    Represents the association between job advertisements and skills.

    Attributes:
        __tablename__ (str): The name of the table in the database.
        job_ad_id (uuid.UUID): The ID of the job advertisement. This is a foreign key referencing the "job_ad" table.
        skill_id (uuid.UUID): The ID of the skill. This is a foreign key referencing the "skill" table.
    """

    __tablename__ = "job_ad_skill"

    job_ad_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_ad.id"),
        nullable=False,
        primary_key=True,
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skill.id"), primary_key=True
    )
