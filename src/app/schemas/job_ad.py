import datetime

from pydantic import BaseModel, condecimal

from app.sql_app.job_ad.job_ad_status import JobAdStatus


class JobAd(BaseModel):
    """
    JobAd schema representing a job advertisement.

    Attributes:
        id (int): Unique identifier for the job advertisement.
        title (str): Title of the job advertisement.
        description (str): Description of the job advertisement.
        min_salary (Decimal): Minimum salary offered for the job. Must be greater than 0, with up to 10 digits and 2 decimal places.
        max_salary (Decimal): Maximum salary offered for the job. Must be greater than 0, with up to 10 digits and 2 decimal places.
        status (JobAdStatus): Current status of the job advertisement.
        created_at (datetime): Timestamp when the job advertisement was created.
        updated_at (datetime): Timestamp when the job advertisement was last updated.
    """
    id: int
    title: str
    description: str
    min_salary: condecimal(gt=0, max_digits=10, decimal_places=2)  # type: ignore
    max_salary: condecimal(gt=0, max_digits=10, decimal_places=2)  # type: ignore
    status: JobAdStatus
    created_at: datetime
    updated_at: datetime
