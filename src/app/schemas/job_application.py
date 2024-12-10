from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.schemas.city import City
from app.schemas.custom_types import Salary
from app.schemas.professional import ProfessionalResponse
from app.schemas.skill import SkillBase, SkillResponse
from app.sql_app.job_application.job_application import JobApplication
from app.sql_app.professional.professional import Professional


class JobStatus(str, Enum):
    """

    Attributes:
        ACTIVE: Appears in Company searches.
        PRIVATE: Can only be seen by the Creator.
        HIDDEN: Accessible only by ID.
    """

    ACTIVE = "active"
    PRIVATE = "private"
    HIDDEN = "hidden"


class JobSearchStatus(str, Enum):
    """

    Attributes:
        ACTIVE: Appears in Company searches.
        MATCHED: Matched with Job Ad.
    """

    ACTIVE = "active"
    MATCHED = "matched"


class MatchResponseRequest(BaseModel):
    accept_request: bool


class JobAplicationBase(BaseModel):
    """
    Pydantic model for creating or updating a professional's job application.

    This model is used to capture the basic information required to reate or update a job application. It includes the required attributes description, application status, and a list of Applicant skills. Optional attributes are minimum and maximum salary range, an city for the application. The data should be passed as a JSON object in the request body.

    Attributes:
        min_salary (int): The lower boundary for the salary range.
        max_salary (int): The upper boundary for the salary range.
        description (str): Description of the professional.
        skills (list[str]): List of Professional Skills.
        city (str): The city the professional is located in.
    """

    name: str = Field(examples=["Job Application"])
    min_salary: float | None = Field(
        ge=0, description="Minimum salary (>= 0)", default=None
    )
    max_salary: float | None = Field(
        ge=0, description="Maximum salary (>= 0)", default=None
    )

    description: str = Field(
        examples=["A seasoned web developer with expertise in FastAPI"]
    )

    @model_validator(mode="before")
    def validate_salary_range(cls, values):
        min_salary = values.get("min_salary")
        max_salary = values.get("max_salary")
        if (min_salary and max_salary) and min_salary > max_salary:
            raise ValueError("min_salary must be less than or equal to max_salary")
        return values

    class Config:
        from_attributes = True


class JobApplicationCreate(JobAplicationBase):
    category_id: UUID = Field(description="Category ID")
    city: str = Field(examples=["Sofia"])
    is_main: bool
    skills: list[SkillBase] = Field(default_factory=list)
    status: JobStatus


class JobApplicationCreateFinal(JobAplicationBase):
    is_main: bool
    skills: list[SkillBase] = Field(default_factory=list)
    status: JobStatus
    city_id: UUID
    professional_id: UUID

    @classmethod
    def create(
        cls,
        job_application_create: JobApplicationCreate,
        city_id: UUID,
        professional_id: UUID,
    ) -> "JobApplicationCreateFinal":
        return cls(
            name=job_application_create.name,
            min_salary=job_application_create.min_salary,
            max_salary=job_application_create.max_salary,
            description=job_application_create.description,
            category_id=job_application_create.category_id,
            city_id=city_id,
            professional_id=professional_id,
            is_main=job_application_create.is_main,
            skills=job_application_create.skills,
            status=job_application_create.status,
        )


class JobApplicationUpdateBase(BaseModel):
    name: str | None = None
    min_salary: Salary | None = None  # type: ignore
    max_salary: Salary | None = None  # type: ignore
    description: str | None = None
    skills: list[SkillBase] | None = Field(default=None)
    is_main: bool | None = Field(default=None)
    application_status: JobStatus | None = Field(default=None)


class JobApplicationUpdate(JobApplicationUpdateBase):
    city: str | None = Field(examples=["Sofia"], default=None)


class JobApplicationUpdateFinal(JobApplicationUpdateBase):
    city_id: UUID | None = None

    @classmethod
    def create(
        cls,
        job_application_update: JobApplicationUpdate,
        city_id: UUID | None = None,
    ) -> "JobApplicationUpdateFinal":
        return cls(
            name=job_application_update.name,
            min_salary=job_application_update.min_salary,
            max_salary=job_application_update.max_salary,
            description=job_application_update.description,
            skills=job_application_update.skills,
            is_main=job_application_update.is_main,
            application_status=job_application_update.application_status,
            city_id=city_id,
        )


class JobApplicationResponse(JobAplicationBase):
    """
    Pydantic schema representing the FastAPI response for Job Application.

    Attributes:
        min_salary (int): The lower boundary for the salary range.
        max_salary (int): The upper boundary for the salary range.
        description (str): Description of the professional.
        category_id (UUID): Category ID.
        skills (list[str]): List of Professional Skills.
        city (str): The city the professional is located in.
        id (UUID): The identifier of the professional.
        first_name (str): First name of the professional.
        last_name (str): Last name of the professional.
        email (EmailStr): Email of the professional.
        description (str): Description of the professional.
        photo bytes | None: Photo of the professional.
    """

    application_id: UUID
    professional_id: UUID
    created_at: datetime
    first_name: str
    last_name: str
    city: str
    email: EmailStr
    photo: bytes | None = None
    status: str
    skills: list[SkillResponse] | None = None
    category_id: UUID
    category_title: str

    @classmethod
    def create(
        cls,
        professional: ProfessionalResponse | Professional,
        job_application: JobApplication,
        skills: list[SkillResponse] | None = None,
    ) -> "JobApplicationResponse":
        city = (
            professional.city.name
            if isinstance(professional, Professional)
            else professional.city
        )
        return cls(
            name=job_application.name,
            application_id=job_application.id,
            professional_id=professional.id,
            created_at=job_application.created_at,
            category_id=job_application.category_id,
            category_title=job_application.category.title,
            photo=professional.photo,
            first_name=professional.first_name,
            last_name=professional.last_name,
            email=professional.email,
            status=job_application.status.value,
            min_salary=job_application.min_salary,
            max_salary=job_application.max_salary,
            description=job_application.description,
            city=city,
            skills=skills,
        )

    class Config:
        json_encoders = {bytes: lambda v: "<binary data>"}
