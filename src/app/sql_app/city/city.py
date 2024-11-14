from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.sql_app.database import Base


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

    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False)
    name = Column(String, nullable=False)

    professionals = relationship("Professional", back_populates="city")
    company_addresses = relationship("CompanyAddress", back_populates="city")
