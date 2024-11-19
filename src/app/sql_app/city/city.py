import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.sql_app.company.company import Company
from app.sql_app.database import Base

if TYPE_CHECKING:
    from app.sql_app import JobAd, JobApplication, Professional


class City(Base):
    """
    City model representing a city in the database.

    Attributes:
        id (uuid.UUID): Unique identifier for the city.
        name (str): Name of the city.
        professionals (list[Professional]): List of professionals associated with the city.
        companies (list[Company]): List of companies associated with the city.
        job_ads (list[JobAd]): List of job advertisements associated with the city.
        job_applications (list[JobApplication]): List of job applications associated with the city.
    """

    __tablename__ = "city"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, unique=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)

    professionals: Mapped[list["Professional"]] = relationship(
        "Professional", back_populates="city", uselist=True, collection_class=list
    )
    companies: Mapped[list["Company"]] = relationship(
        "Company", back_populates="city", uselist=True, collection_class=list
    )
    job_ads: Mapped[list["JobAd"]] = relationship(
        "JobAd", back_populates="location", uselist=True, collection_class=list
    )
    job_applications: Mapped[list["JobApplication"]] = relationship(
        "JobApplication", back_populates="city", uselist=True, collection_class=list
    )
