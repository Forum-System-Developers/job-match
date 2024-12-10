from uuid import UUID

from pydantic import BaseModel, Field

from app.services.enums.match_status import MatchStatus


class MatchResponse(BaseModel):
    """
    MatchResponse schema for job matching responses.

    Attributes:
        job_ad_id (UUID): The ID of the job ad that was matched.
        job_application_id (UUID): The ID of the job application that was matched.
        status (JobAdStatus): The status of the match response.
    """

    job_ad_id: UUID = Field(description="The ID of the job ad that was matched.")
    job_application_id: UUID = Field(
        description="The ID of the job application that was matched."
    )
    status: MatchStatus = Field(description="The status of the match response.")

    class Config:
        from_attributes = True


class MatchRequestCreate(MatchResponse):
    pass


class MatchRequestAd(MatchResponse):
    """
    MatchRequest schema for job matching requests.

    Attributes:
        job_ad_id (UUID): The ID of the job ad that was matched.
        job_application_id (UUID): The ID of the job application that was matched.
        status (JobAdStatus): The status of the match response.
        title (str): The title of the job ad.
        description (str): The description of the job ad.
        company_id (UUID): The ID of the company that was matched.
        company_name (str): The name of the company that was matched.
        min_salary (float): The minimum salary for the job ad.
        max_salary (float): The maximum salary for the job ad.
    """

    title: str = Field(description="The title of the job ad.")
    description: str = Field(description="The description of the job ad.")
    company_id: UUID = Field(description="The ID of the company that was matched.")
    company_name: str = Field(description="The name of the company that was matched.")
    min_salary: float = Field(description="The minimum salary for the job ad.")
    max_salary: float = Field(description="The maximum salary for the job ad.")

    class Config:
        from_attributes = True


class MatchRequestApplication(MatchResponse):
    """
    MatchRequest schema for job matching requests.

    Attributes:
        job_ad_id (UUID): The ID of the job ad that was matched.
        job_application_id (UUID): The ID of the job application that was matched.
        status (JobAdStatus): The status of the match response.
        name (str): The name of the job application.
        description (str): The description of the job application.
        professional_id (UUID): The ID of the professional that was matched.
        professional_first_name (str): The first name of the professional that was matched.
        professional_last_name (str): The last name of the professional that was matched.
        min_salary (float): The minimum salary for the job ad.
        max_salary (float): The maximum salary for the job ad.
    """

    name: str = Field(description="The title of the job application.")
    description: str = Field(description="The description of the job application.")
    professional_id: UUID = Field(
        description="The ID of the professional that was matched."
    )
    professional_first_name: str = Field(
        description="The name of the professional that was matched."
    )
    professional_last_name: str = Field(
        description="The name of the professional that was matched."
    )
    min_salary: float = Field(description="The minimum salary for the job application.")
    max_salary: float = Field(description="The maximum salary for the job application.")

    class Config:
        from_attributes = True
