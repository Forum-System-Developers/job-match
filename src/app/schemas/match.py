from uuid import UUID

from pydantic import BaseModel, Field

from app.services.enums.match_status import MatchStatus
from app.sql_app import Match
from app.sql_app.job_ad.job_ad import JobAd
from app.sql_app.job_application.job_application import JobApplication
from app.sql_app.professional.professional import Professional


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

    @classmethod
    def create_response(cls, match: Match, job_ad: JobAd) -> "MatchRequestAd":
        """
        Create a MatchRequest object from a Match object.

        Args:
            match (Match): The Match object to create a MatchRequest object from.
            job_ad (JobAd): The JobAd object to create a MatchRequest object from.

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

    @classmethod
    def create_response(
        cls, match: Match, job_application: JobApplication
    ) -> "MatchRequestApplication":
        """
        Create a MatchRequest object from a Match object.

        Args:
            match (Match): The Match object to create a MatchRequest object from.
            job_application (JobApplication): The JobApplication object to create a MatchRequest object from.

        Returns:
            MatchRequest: The created MatchRequest object.
        """

        return cls(
            name=job_application.name,
            description=job_application.description,
            job_ad_id=match.job_ad_id,
            job_application_id=match.job_application_id,
            status=match.status,
            professional_id=job_application.professional_id,
            professional_first_name=job_application.professional.first_name,
            professional_last_name=job_application.professional.last_name,
            min_salary=job_application.min_salary,
            max_salary=job_application.max_salary,
        )
