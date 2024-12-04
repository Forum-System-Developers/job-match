from uuid import UUID

from pydantic import BaseModel, Field

from app.sql_app import Match
from app.sql_app.job_ad.job_ad import JobAd
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

    @classmethod
    def create_response(cls, match: Match, job_ad: JobAd) -> "MatchRequestAd":
        """
        Create a MatchRequest object from a Match object.

        Args:
            match (Match): The Match object to create a MatchRequest object from.

        Returns:
            MatchRequest: The created MatchRequest object.
        """

        return cls(
            title=job_ad.title,
            description=job_ad.description,
            job_ad_id=match.job_ad_id,
            job_application_id=match.job_application_id,
            status=match.status,
            company_id=job_ad.company_id,
            company_name=job_ad.company.name,
            min_salary=job_ad.min_salary,
            max_salary=job_ad.max_salary,
        )
