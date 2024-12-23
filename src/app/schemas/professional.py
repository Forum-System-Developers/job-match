import re
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.custom_types import Password, Username
from app.schemas.job_ad import JobAdPreview
from app.schemas.match import MatchRequestAd
from app.schemas.skill import SkillResponse
from app.services.enums.professional_status import ProfessionalStatus


class PrivateMatches(BaseModel):
    status: bool


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
        sub (str): The google token unique identifier of the professional.
        username (Username): Username of the professional.
        password (Password): Password for the professional profile..
        email (EmailStr): Email of the professional.
    """

    sub: str | None = None
    username: Username = Field(examples=["username"])  # type: ignore
    password: Password = Field(examples=["password"])  # type:ignore
    email: EmailStr = Field(examples=["email"])

    @field_validator("password")
    def _validate_password(cls, value: str) -> str:
        if not re.match(
            r"^(?=.*\d)(?=.*[!@#$%^&*()\-_=+\\|;:'\",.<>/?]).{8,}$",
            value,
        ):
            raise ValueError(
                "Password must be at least 8 characters long, contain at least one uppercase letter, one lowercase letter, one digit, and one special character."
            )
        return value

    class Config:
        from_attributes = True


class ProfessionalCreateFinal(BaseModel):
    sub: str | None = None
    username: Username  # type: ignore
    password_hash: str
    first_name: str
    last_name: str
    email: EmailStr
    description: str
    city_id: UUID


class ProfessionalUpdateBase(BaseModel):
    first_name: str | None = Field(examples=["Jane"], default=None)
    last_name: str | None = Field(examples=["Doe"], default=None)
    description: str | None = Field(
        examples=["A seasoned web developer with expertise in FastAPI"], default=None
    )


class ProfessionalUpdate(ProfessionalUpdateBase):
    city: str | None = Field(examples=["Sofia"], default=None)


class ProfessionalUpdateFinal(ProfessionalUpdateBase):
    city_id: UUID | None = Field(description="City ID", default=None)
    status: ProfessionalStatus | None = Field(examples=["active"], default=None)


class ProfessionalResponse(ProfessionalBase):
    """
    Pydantic schema representing the FastAPI response for Professional.

    Attributes:
        id (UUID): Unique identifier of the professional.
        first_name (str): First name of the professional.
        last_name (str): Last name of the professional.
        description (str): Description of the professional.
        photo bytes | None: Photo of the professional.
        active_application_count (int): Number of active applications.
        city (str): The city the professional is located in.
        status (ProfessionalStatus): Status of the professional.
        skills (list[SkillResponse]): List of skills associated with the professional.
        matched_ads (list[JobAdPreview] | None): List of matched
                job advertisements or None if the professional has private matches.


    """

    id: UUID
    email: EmailStr
    photo: bytes | None = None
    status: ProfessionalStatus
    skills: list[SkillResponse] = []
    active_application_count: int
    matched_ads: list[JobAdPreview] | None = None
    sent_match_requests: list[MatchRequestAd] | None = None

    class Config:
        json_encoders = {bytes: lambda v: "<binary data>"}


class ProfessionalRequestBody(BaseModel):
    professional: ProfessionalCreate
    status: ProfessionalStatus


class ProfessionalUpdateRequestBody(BaseModel):
    professional: ProfessionalUpdate
    status: ProfessionalStatus
