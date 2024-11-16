from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.sql_app.database import Base


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

    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False)
    city_id = Column(UUID(as_uuid=True), ForeignKey("city.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("company.id"), nullable=False)
    address = Column(String, nullable=False)

    city = relationship("City", back_populates="company_addresses")
    company_address = relationship("Company", back_populates="company_addresses")
