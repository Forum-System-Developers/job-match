from uuid import UUID

from pydantic import BaseModel, Field

from app.sql_app.job_ad.job_ad_status import JobAdStatus


class MatchRequest(BaseModel):
    """
    MatchRequest schema for job matching requests.

    Attributes:
        job_ad_id (UUID): The ID of the job ad to match against.
        job_application_id (UUID): The ID of the job application to match against.
        status (JobAdStatus): The status of the match request.
    """

    job_ad_id: UUID = Field(description="The ID of the job ad to match against.")
    job_application_id: UUID = Field(
        description="The ID of the job application to match against."
    )
    status: JobAdStatus = Field(description="The status of the match request.")
