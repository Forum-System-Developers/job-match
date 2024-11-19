import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.sql_app.database import Base

if TYPE_CHECKING:
    from app.sql_app.category.category import Category
    from app.sql_app.job_application.job_application import JobApplication


class CategoryJobApplication(Base):
    """
    Junction table representing the relationship between multiple Categories and Job Applications.

    Attributes:
        category_id (UUID): The identifier of the category.
        job_application_id (UUID): The identifier of the Job Application.

    Relationships:
        category (Category): The referenced Category.
        job_application (JobApplication): The referenced Job Application.
    """

    __tablename__ = "category_job_application"

    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("category.id"), nullable=False, primary_key=True
    )
    job_application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_application.id"),
        nullable=False,
        primary_key=True,
    )

    category: Mapped["Category"] = relationship(
        "Category", back_populates="category_job_applications"
    )
    job_application: Mapped["JobApplication"] = relationship(
        "JobApplication", back_populates="category_job_applications"
    )
