from uuid import UUID

from pydantic import BaseModel, Field

from app.sql_app import Match
from app.sql_app.match.match_status import MatchStatus


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

    @classmethod
    def create(cls, match: Match) -> "MatchResponse":
        """
        Create a MatchResponse object from a Match object.

        Args:
            match (Match): The Match object to create a MatchResponse object from.

        Returns:
            MatchResponse: The created MatchResponse object.
        """
        return cls(
            job_ad_id=match.job_ad_id,
            job_application_id=match.job_application_id,
            status=match.status,
        )
