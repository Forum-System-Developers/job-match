from typing import Optional

from pydantic import BaseModel, Field

from app.sql_app.professional.professional_status import ProfessionalStatus


class ProfessionalBase(BaseModel):
    """
    Request body model for creating or updating a professional's profile.

    This model is used to capture the basic information of a professional when
    creating or updating their profile. It includes required attributes such as
    the first name, last name, and description of the professional. The data
    should be passed as a JSON object in the request body.

    Attributes:
        first_name (str): First name of the professional.
        last_name (str): Last name of the professional.
        description (str): Description of the professional.
        city (str): The city the professional is located in.
    """

    first_name: str = Field(examples=["Jane"])
    last_name: str = Field(examples=["Doe"])
    description: str = Field(
        examples=["A seasoned web developer with expertise in FastAPI"]
    )
    city: str = Field(examples=["Sofia"])

    class Config:
        from_attributes = True


class ProfessionalResponse(ProfessionalBase):
    """
    Pydantic schema representing the FastAPI response for Professional.

    Attributes:
        first_name (str): First name of the professional.
        last_name (str): Last name of the professional.
        description (str): Description of the professional.
        photo Optional[bytes]: Photo of the professional.
        active_application_count (int): Number of active applications.
    """

    photo: Optional[bytes] = None
    status: ProfessionalStatus
    active_application_count: int

    class Config:
        from_attributes = True


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
        def get_items(filter_params: Annotated[FilterParams, Query] = FilterParams()):
            ...
        ```
    """

    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
