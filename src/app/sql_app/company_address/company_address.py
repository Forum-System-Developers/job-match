from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.sql_app.database import Base

if TYPE_CHECKING:
    from app.sql_app.city.city import City
    from app.sql_app.company.company import Company


class CompanyAddress(Base):
    """
    Represents a company address model.

    Attributes:
        id (UUID): Unique identifier for the company address.
        city_id (UUID): Foreign key referencing the city.
        company_id (UUID): Foreign key referencing the company.
        address (str): The address of the company.
    Relationships:
        city (relationship): Relationship to the City model.
        company_address (relationship): Relationship to the Company model.
    """

    __tablename__ = "company_address"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        nullable=False,
        uselist=True,
        collection_class=list,
    )
    city_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("city.id"), nullable=False
    )
    company_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("company.id"), nullable=False
    )
    address: Mapped[str] = mapped_column(String, nullable=False)

    city: Mapped["City"] = relationship("City", back_populates="company_addresses")
    company_address: Mapped["Company"] = relationship(
        "Company", back_populates="company_addresses"
    )
