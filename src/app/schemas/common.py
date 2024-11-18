from typing import Literal

from pydantic import BaseModel, Field

from app.sql_app.job_ad.job_ad_status import JobAdStatus


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
    skills: list[str] = Field(
        examples=[["Python", "Linux", "React"]],
        default=[],
        description="List a set of skills to be included in the search",
    )
    job_application_status: JobAdStatus = Field(
        description="ACTIVE: Represents an active job application. ARCHIVED: Represents a matched/archived job application",
        default=JobAdStatus.ACTIVE,
    )


# TODO Add a Base class for JobAdSearchParams
class JobAdSearchParams(BaseModel):
    """
    JobAdSearchParams defines the parameters for searching job advertisements.

    Attributes:
        order (Literal["asc", "desc"]): The order of the search results. Default is "desc".
        order_by (Literal["created_at", "updated_at"]): The field by which to order the search results. Default is "created_at".
        title (str): The title of the job ad.
        min_salary (int): Minimum salary.
        max_salary (int): Maximum salary.
        company_id (str): The company ID.
        location_id (str): The location ID.
        skills (list[str]): List of skills to be included in the search. Default is an empty list.
        job_ad_status (JobAdStatus): The status of the job ad. Default is JobAdStatus.ACTIVE.
    """

    order: Literal["asc", "desc"] = "desc"
    order_by: Literal["created_at", "updated_at"] = "created_at"
    title: str = Field(description="The title of the job ad")
    min_salary: int = Field(description="Minimum salary")
    max_salary: int = Field(description="Maximum salary")
    company_id: str = Field(description="The company ID")
    location_id: str = Field(description="The location ID")
    skills: list[str] = Field(
        examples=[["FastAPI", "Django", "Flask"]],
        default=[],
        description="List of skills to be included in the search",
    )
    job_ad_status: JobAdStatus = Field(
        description="ACTIVE: Represents an active job ad. ARCHIVED: Represents an archived job ad",
        default=JobAdStatus.ACTIVE,
    )
