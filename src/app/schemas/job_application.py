from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.schemas.professional import ProfessionalResponse
from app.sql_app.job_application.job_application import JobApplication
from app.sql_app.professional.professional import Professional


class JobStatus(str, Enum):
    ACTIVE = "acitve"
    PRIVATE = "private"
    HIDDEN = "hidden"


class JobAplicationBase(BaseModel):
    """
    Model for creating or updating a professional's job application.

    This model is used to capture the basic information required to reate or update a job application. It includes the required attributes description, application status, and a list of Applicant skills. Optional attributes are minimum and maximum salary range, an city for the application. The data should be passed as a JSON object in the request body.

    Attributes:
        min_salary (int): The lower boundary for the salary range.
        max_salary (int): The upper boundary for the salary range.
        description (str): Description of the professional.
        skills (list[str]): List of Professional Skills.
        city (str): The city the professional is located in.
    """

    min_salary: float | None = Field(
        ge=0, description="Minimum salary (>= 0)", default=None
    )
    max_salary: float | None = Field(
        ge=0, description="Maximum salary (>= 0)", default=None
    )

    description: str = Field(
        examples=["A seasoned web developer with expertise in FastAPI"]
    )
    skills: list[str] = Field(examples=[["Python", "Linux", "React"]])
    city: str | None = Field(examples=["Sofia"], default=None)

    @model_validator(mode="before")
    def validate_salary_range(cls, values):
        min_salary = values.get("min_salary")
        max_salary = values.get("max_salary")
        if (min_salary and max_salary) and min_salary > max_salary:
            raise ValueError("min_salary must be less than or equal to max_salary")
        return values

    class Config:
        from_attributes = True


class JobApplicationResponse(JobAplicationBase):
    """
    Pydantic schema representing the FastAPI response for Job Application.

    Attributes:
        min_salary (int): The lower boundary for the salary range.
        max_salary (int): The upper boundary for the salary range.
        description (str): Description of the professional.
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
    first_name: str
    last_name: str
    email: EmailStr
    photo: Optional[bytes] = None
    status: str

    @classmethod
    def create(
        cls,
        professional: ProfessionalResponse | Professional,
        job_application: JobApplication,
        city: str,
    ) -> "JobApplicationResponse":
        return cls(
            application_id=job_application.id,
            profesisonal_id=professional.id,
            photo=professional.photo,
            first_name=professional.first_name,
            last_name=professional.last_name,
            email=professional.email,
            status=job_application.status.value,
            min_salary=job_application.min_salary,
            max_salary=job_application.max_salary,
            description=job_application.description,
            city=city,
            skills=job_application.skills,  # TODO
        )
