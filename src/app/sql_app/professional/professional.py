from sqlalchemy import Column, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.sql_app.database import Base
from app.sql_app.professional.professional import ProfessionalType


class Professional(Base):
    """
    Represents a professional model.

    Attributes:
        id (UUID): Unique identifier for the professional, generated by the server.
        user_id (UUID): Foreign key referencing the user associated with the professional.
        cities_id (UUID): Identifier for the city associated with the professional.
        description (str): Description of the professional.
        photo (str, optional): URL or path to the professional's photo.
        status (ProfessionalType): Status of the professional, represented as an enum.
        active_application_count (int, optional): Count of active job applications by the professional.
        first_name (str): First name of the professional.
        last_name (str): Last name of the professional.

    Relationships:
        user (relationship): Relationship to the User model.
        city (relationship): Relationship to the City model.
        job_applications (relationship): Relationship to the JobApplication model.
    """

    __tablename__ = "professionals"

    id = Column(
        UUID(as_uuid=True),
        server_default=func.uuid_generate_v4(),
        primary_key=True,
        unique=True,
        nullable=False,
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    cities_id = Column(UUID(as_uuid=True), nullable=False)
    description = Column(String, nullable=False)
    photo = Column(String, nullable=True)
    status = Column(Enum(ProfessionalType), nullable=False)
    active_application_count = Column(Integer, nullable=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    user = relationship("User", back_populates="professional")
    city = relationship("City", back_populates="professionals")
    job_applications = relationship("JobApplication", back_populates="professional")
