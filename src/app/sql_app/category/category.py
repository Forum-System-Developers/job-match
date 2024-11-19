import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.sql_app.database import Base

if TYPE_CHECKING:
    from app.sql_app import JobAd
    from app.sql_app.category_job_application.category_job_application import (
        CategoryJobApplication,
    )


class Category(Base):
    """
    Represents a Category entity in the app.

    Attributes:
        id (UUID): The unique identifier of the Category.
        title (str): The title of the Category.
        description (str): The description of the Category.


    Relationships:
        professional (Professional): The user who created the job application.
        category (Category): The category for the Job Ad that was matched with the Job Application.
        skills (list[Skill]): The skillset indicated on this job application.
    """

    __tablename__ = "category"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        server_default=func.uuid_generate_v4(),
        primary_key=True,
        unique=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    description = mapped_column(String, nullable=False)

    job_ads: Mapped[list["JobAd"]] = relationship(
        "JobAd", back_populates="category", uselist=True, collection_class=list
    )
    category_job_applications: Mapped[list["CategoryJobApplication"]] = relationship(
        "CategoryJobApplication",
        back_populates="category",
        uselist=True,
        collection_class=list,
    )
