from enum import Enum
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, model_validator
from sqlalchemy.orm import Session

from app.schemas.city import City
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
    category_id: UUID = Field(description="Category ID")

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
    city: str = Field(examples=["Sofia"])
    is_main: bool
    skills: list[SkillBase] = Field(default_factory=list)
    status: JobStatus


class JobApplicationUpdate(JobAplicationBase):
    city: str | None = Field(examples=["Sofia"], default=None)
    skills: list[SkillBase] | None = Field(default=None)
    is_main: bool
    application_status: JobStatus


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

    id: UUID
    professional_id: UUID
    first_name: str
    last_name: str
    city: City
    email: EmailStr
    photo: bytes | None = None
    status: str
    skills: list[SkillResponse] | None = None
    category_title: str

    @classmethod
    def create(
        cls,
        professional: ProfessionalResponse | Professional,
        job_application: JobApplication,
        db: Session,
        skills: list[SkillResponse] | None = None,
    ) -> "JobApplicationResponse":
        from app.services import job_application_service

        city = (
            professional.city.name
            if isinstance(professional, Professional)
            else professional.city
        )
        if skills is None:
            skills = job_application_service.get_skills(
                job_application=job_application, db=db
            )
        return cls(
            id=job_application.id,
            name=job_application.name,
            professional_id=professional.id,
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
