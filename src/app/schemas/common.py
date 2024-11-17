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
