import uuid
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
    Represents a company address in the database.

    Attributes:
        id (UUID): The unique identifier for the company address.
        city_id (UUID): The foreign key referencing the city.
        company_id (UUID): The foreign key referencing the company.
        address (str): The address of the company.

    Relationships:
        city (City): The relationship to the City model.
        company (Company): The relationship to the Company model.
    """

    __tablename__ = "company_address"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        nullable=False,
        collection_class=list,
    )
    city_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("city.id"), nullable=False
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("company.id"), nullable=False
    )
    address: Mapped[str] = mapped_column(String, nullable=False)

    city: Mapped["City"] = relationship("City", back_populates="company_addresses")
    company: Mapped["Company"] = relationship("Company", back_populates="addresses")
