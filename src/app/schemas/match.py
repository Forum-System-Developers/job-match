from uuid import UUID

from pydantic import BaseModel, Field

from app.sql_app.job_ad.job_ad_status import JobAdStatus


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
    status: JobAdStatus = Field(description="The status of the match response.")


class AcceptRequestMatchResponse(BaseModel):
    message: str = "Match request accepted successfully."
