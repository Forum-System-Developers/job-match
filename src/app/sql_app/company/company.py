from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.sql_app.database import Base


class Company(Base):
    """
    Represents a company entity in the database.

    Attributes:
        id (UUID): Unique identifier for the company, generated by the server.
        user_id (UUID): Foreign key referencing the user who owns the company.
        description (str): Description of the company.
        name (str): Name of the company, with a maximum length of 50 characters.
        email (str): Unique email address of the company, with a maximum length of 255 characters.
        phone_number (str): Unique phone number of the company, with a maximum length of 25 characters.
        logo (str): URL or path to the company's logo.
        active_job_count (int, optional): Number of active job postings by the company.
        successfull_matches_count (int, optional): Number of successful job matches made by the company.
        created_at (datetime): Timestamp when the company record was created.
        updated_at (datetime, optional): Timestamp when the company record was last updated.

    Relationships:
        user (User): The user who owns the company.
        address (CompanyAddress): The address associated with the company.
        job_ads (JobAd): The job advertisements posted by the company.
    """

    __tablename__ = "company"

    id = Column(
        UUID(as_uuid=True),
        server_default=func.uuid_generate_v4(),
        primary_key=True,
        unique=True,
        nullable=False,
    )
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("user.id"), unique=True, nullable=False
    )
    description = Column(String, nullable=False)
    name = Column(String(50), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone_number = Column(String(25), unique=True, nullable=False)
    logo = Column(String, nullable=False)
    active_job_count = Column(Integer, nullable=True)
    successfull_matches_count = Column(Integer, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=True,
    )

    user = relationship("User", back_populates="company")
    address = relationship("CompanyAddress", back_populates="company")
    job_ads = relationship("JobAd", back_populates="company")
