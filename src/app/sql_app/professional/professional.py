import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Integer, LargeBinary, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.sql_app.database import Base
from app.sql_app.professional.professional_status import ProfessionalStatus

if TYPE_CHECKING:
    from app.sql_app.city.city import City
    from app.sql_app.job_application.job_application import JobApplication


class Professional(Base):
    """
    Represents a professional in the job matching application.

    Attributes:
        id (UUID): Unique identifier for the professional.
        city_id (UUID): Foreign key referencing the city where the professional is located.
        username (str): Unique username for the professional.
        password (str): Password for the professional.
        description (str): Description of the professional.
        email (str): Unique email address of the professional.
        photo (bytes, optional): Photo of the professional.
        status (ProfessionalStatus): Current status of the professional.
        active_application_count (int): Number of active job applications by the professional.
        first_name (str): First name of the professional.
        last_name (str): Last name of the professional.

    Relationships:
        city (City): Relationship to the City model.
        job_applications (List[JobApplication]): Relationship to the JobApplication model.
    """

    __tablename__ = "professional"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        server_default=func.uuid_generate_v4(),
        primary_key=True,
        unique=True,
        nullable=False,
    )
    city_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("city.id"), nullable=False
    )
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    photo: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    status: Mapped[ProfessionalStatus] = mapped_column(
        Enum(ProfessionalStatus, native_enum=True), nullable=False
    )
    active_application_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)

    city: Mapped["City"] = relationship("City", back_populates="professionals")
    job_applications: Mapped["JobApplication"] = relationship(
        "JobApplication",
        back_populates="professional",
        uselist=True,
        collection_class=list,
    )
