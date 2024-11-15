from typing import Optional

from pydantic import BaseModel, Field


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

    """

    first_name: str = Field(example="Jane")
    last_name: str = Field(example="Doe")
    description: str = Field(
        example="A seasoned web developer with expertise in FastAPI"
    )


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
    active_application_count: int
