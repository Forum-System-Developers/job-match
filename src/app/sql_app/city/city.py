import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.sql_app.database import Base

if TYPE_CHECKING:
    from app.sql_app.company_address.company_address import CompanyAddress
    from app.sql_app.job_ad.job_ad import JobAd
    from app.sql_app.job_application.job_application import JobApplication
    from app.sql_app.professional.professional import Professional


class City(Base):
    """
    Represents a city model.

    Attributes:
        id (UUID): Unique identifier for the city.
        name (str): Name of the city.

    Reletionships:
        professionals (relationship): Relationship to the Professional model.
        company_addresses (relationship): Relationship to the CompanyAddress model.
    """

    __tablename__ = "city"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, unique=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)

    professionals: Mapped["Professional"] = relationship(
        "Professional", back_populates="city", uselist=True, collection_class=list
    )
    company_addresses: Mapped["CompanyAddress"] = relationship(
        "CompanyAddress", back_populates="city", uselist=True, collection_class=list
    )
    job_ads: Mapped["JobAd"] = relationship(
        "JobAd", back_populates="location", uselist=True, collection_class=list
    )
    job_applications: Mapped["JobApplication"] = relationship(
        "JobApplication", back_populates="city", uselist=True, collection_class=list
    )
