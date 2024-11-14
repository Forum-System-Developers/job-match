from sqlalchemy import Column, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.app.sql_app.database import Base


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

    id = Column(
        UUID(as_uuid=True),
        server_default=func.uuid_generate_v4(),
        primary_key=True,
        unique=True,
        nullable=False,
    )
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)

    job_ads = relationship("JobAd", back_populates="category")
    job_applications = relationship("JobApplication", back_populates="category")
