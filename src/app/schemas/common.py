from typing import Literal
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel, Field, field_validator

from app.services.enums.job_ad_status import JobAdStatus


class FilterParams(BaseModel):
    """
    Pydantic schema for pagination and filtering parameters.

    This schema is designed to handle standard query parameters
    for limiting and offsetting results in paginated responses.

    Attributes:
        limit (int): The maximum number of records to return.
            - Default: 100
            - Constraints: Must be greater than 0 and less than or equal to 100.
        offset (int): The number of records to skip before starting to return results.
            - Default: 0
            - Constraints: Must be greater than or equal to 0.

    Example:
        Use this schema in FastAPI endpoints to simplify pagination:

        ```
        @app.get("/items/")
        def get_items (FilterParams = Depends()):
            ...
        ```
    """

    limit: int = Field(default=10, gt=0, le=100)
    offset: int = Field(default=0, ge=0)


class SearchParams(BaseModel):
    """
    Pydantic schema for search parameters.

    This schema is designed to handle search parameters for filtering
    and ordering results in paginated responses.

    Attributes:
     order (Literal["asc", "desc"]): The order in which to return results.
        - Default: "desc"
        - Constraints: Must be either "asc" or "desc".
    order_by (Literal["created_at", "updated_at"]): The field to order results by.
        - Default: "created_at"
        - Constraints: Must be either "created_at" or "updated_at".
    skills (list[str]): A list of skills to filter the results by.
        - Default: []
        - Constraints: Must be a list of strings.
    job_application_status (JobAdStatus): The status of the job application.
        - Default: JobAdStatus.ACTIVE
        - Constraints: Must be either JobAdStatus.ACTIVE or JobAdStatus.ARCHIVED.


    Example:
        Use this schema in FastAPI endpoints to simplify search queries:

        ```
        @app.get("/items/")
        def get_items (search_params: SearchParams = Depends()):
            ...
        ```
    """

    order: Literal["asc", "desc"] = "desc"
    order_by: Literal["created_at", "updated_at"] = "created_at"


class SearchJobApplication(SearchParams):
    """
    Pydantic schema for search parameters for Job Applications.

    This schema is designed to handle search parameters for filtering
    and ordering results in paginated responses.

    Attributes:
     order (Literal["asc", "desc"]): The order in which to return results.
        - Default: "desc"
        - Constraints: Must be either "asc" or "desc".
    order_by (Literal["created_at", "updated_at"]): The field to order results by.
        - Default: "created_at"
        - Constraints: Must be either "created_at" or "updated_at".
    skills (list[str]): A list of skills to filter the results by.
        - Default: []
        - Constraints: Must be a list of strings.
    job_application_status (JobAdStatus): The status of the job application.
        - Default: JobAdStatus.ACTIVE
        - Constraints: Must be either JobAdStatus.ACTIVE or JobAdStatus.ARCHIVED.


    Example:
        Use this schema in FastAPI endpoints to simplify search queries:

        ```
        @app.get("/items/")
        def get_items (search_params: SearchParams = Depends()):
            ...
        ```
    """

    job_application_status: JobAdStatus = Field(
        description="ACTIVE: Represents an active job application. ARCHIVED: Represents a matched/archived job application",
        default=JobAdStatus.ACTIVE,
    )


class JobAdSearchParams(SearchParams):
    """
    JobAdSearchParams is a data model for defining the parameters used in searching job advertisements.

    Attributes:
        title (str | None): The title of the job ad. Default is None.
        salary_threshold (float): The salary threshold. Must be greater than or equal to 0. Default is 0.
        min_salary (float | None): The minimum salary. Must be non-negative and less than or equal to max_salary if provided. Default is None.
        max_salary (float | None): The maximum salary. Default is None.
        company_id (UUID | None): The company ID. Default is None.
        location_id (UUID | None): The location ID. Default is None.
        job_ad_status (JobAdStatus): The status of the job ad. Can be ACTIVE or ARCHIVED. Default is JobAdStatus.ACTIVE.
        skills (list[str]): A list of skills to be included in the search. Default is an empty list.
        skills_threshold (int): The skills threshold. Must be between 0 and the number of skills. Default is 0.
    """

    title: str | None = Field(description="The title of the job ad", default=None)
    salary_threshold: float = Field(description="The salary threshold", ge=0, default=0)
    min_salary: float | None = Field(description="Minimum salary", default=None)
    max_salary: float | None = Field(description="Maximum salary", default=None)
    company_id: UUID | None = Field(description="The company ID", default=None)
    location_id: UUID | None = Field(description="The location ID", default=None)
    job_ad_status: JobAdStatus = Field(
        description="ACTIVE: Represents an active job ad. ARCHIVED: Represents an archived job ad",
        default=JobAdStatus.ACTIVE,
    )
    skills: list[str] = Field(
        examples=[["Python", "Linux", "React"]],
        default=[],
        description="List a set of skills to be included in the search",
    )
    skills_threshold: int = Field(description="The skills threshold", ge=0, default=0)

    @field_validator("min_salary")
    def validate_min_salary(cls, value, values):
        if value is not None:
            if value < 0:
                raise ValueError("Minimum salary must be non-negative")
            max_salary = values.data.get("max_salary")
            if max_salary is not None and value > max_salary:
                raise ValueError("Minimum salary cannot be greater than maximum salary")
        return value

    @field_validator("skills_threshold")
    def validate_skills_threshold(cls, value, values):
        if value is not None:
            skills = values.data.get("skills", [])
            if not 0 <= value <= len(skills):
                raise ValueError(
                    "Skills threshold must be between 0 and the number of skills"
                )
        return value


class MessageResponse(BaseModel):
    """
    Message schema for returning messages in responses.

    Attributes:
        message (str): The message to return.
    """

    message: str = Field(description="The message to return")
