import re
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.custom_types import Password, Username
from app.sql_app.professional.professional import Professional
from app.sql_app.professional.professional_status import ProfessionalStatus


class ProfessionalBase(BaseModel):
    first_name: str = Field(examples=["Jane"])
    last_name: str = Field(examples=["Doe"])
    description: str = Field(
        examples=["A seasoned web developer with expertise in FastAPI"]
    )
    city: str = Field(examples=["Sofia"])


class ProfessionalCreate(ProfessionalBase):
    """
    Request body model for creating or updating a professional's profile.

    This model is used to capture the basic information of a professional when
    creating or updating their profile. It includes required attributes such as
    the first name, last name, and description of the professional. The data
    should be passed as a JSON object in the request body.

    Attributes:
        username (Username): Username of the professional.
        password (Password): Password for the professional profile..
        email (EmailStr): Email of the professional.
    """

    username: Username = Field(examples=["username"])  # type: ignore
    password: Password = Field(examples=["password"])  # type:ignore
    email: EmailStr = Field(examples=["email"])

    @field_validator("password")
    def _validate_password(cls, value) -> str:
        if not re.match(
            r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()\-_=+\\|;:\'",.<>/?])$'
        ):
            raise ValueError(
                "Password must be at least 8 characters long, contain at least one uppercase letter, one lowercase letter, one digit, and one special character."
            )
        return value

    class Config:
        from_attributes = True


class ProfessionalResponse(ProfessionalBase):
    """
    Pydantic schema representing the FastAPI response for Professional.

    Attributes:
        first_name (str): First name of the professional.
        last_name (str): Last name of the professional.
        description (str): Description of the professional.
        photo bytes | None: Photo of the professional.
        active_application_count (int): Number of active applications.
        city (str): The city the professional is located in.

    """

    id: UUID
    email: EmailStr
    photo: bytes | None = None
    status: ProfessionalStatus
    active_application_count: int

    @classmethod
    def create(cls, professional: Professional, city: str) -> "ProfessionalResponse":
        return cls(
            id=professional.id,
            first_name=professional.first_name,
            last_name=professional.last_name,
            email=professional.email,
            description=professional.description,
            photo=professional.photo,
            status=professional.status,
            active_application_count=professional.active_application_count,
            city=city,
        )
