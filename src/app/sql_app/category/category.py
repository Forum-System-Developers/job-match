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
    Represents a category in the job matching application.

    Attributes:
        id (uuid.UUID): Unique identifier for the category, generated by the server.
        title (str): Title of the category.
        description (str): Description of the category.
        job_ads (list[JobAd]): List of job advertisements associated with this category.
        category_job_applications (list[CategoryJobApplication]): List of category job applications associated with this category.
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
