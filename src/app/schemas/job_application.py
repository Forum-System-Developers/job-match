from typing import Optional

from pydantic import BaseModel, Field, model_validator
from app.sql_app.job_application.job_application_status import JobStatus


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

    min_salary: int | None = Field(ge=0, description="Minimum salary (>= 0)")
    max_salary: int | None = Field(ge=0, description="Maximum salary (>= 0)")

    description: str = Field(
        examples=["A seasoned web developer with expertise in FastAPI"]
    )
    skills: list[str] = Field(examples=[["Python", "Linux", "React"]])
    city: str | None = Field(examples=["Sofia"])

    @model_validator(mode="before")
    def validate_salary_range(cls, values):
        min_salary = values.get("min_salary")
        max_salary = values.get("max_salary")
        if min_salary > max_salary:
            raise ValueError("min_salary must be less than or equal to max_salary")
        return values

    class Config:
        from_attributes = True


class JobApplicationResponse(JobAplicationBase):
    """
    Pydantic schema representing the FastAPI response for Job Application.

    Attributes:
        first_name (str): First name of the professional.
        last_name (str): Last name of the professional.
        description (str): Description of the professional.
        photo bytes | None: Photo of the professional.
        active_application_count (int): Number of active applications.
    """

    photo: Optional[bytes] = None
    status: JobStatus
    active_application_count: int

    class Config:
        from_attributes = True
