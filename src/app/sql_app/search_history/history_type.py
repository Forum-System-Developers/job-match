from enum import Enum


class HistoryType(Enum):
    """
    HistoryType is an enumeration that represents different types of history records.

    Attributes:
        job_application (str): Represents a job application history type.
        job_ad (str): Represents a job advertisement history type.
        company (str): Represents a company history type.
        professional (str): Represents a professional history type.
    """

    JOB_APPLICATION = "job_application"
    JOB_AD = "job_ad"
    COMPANY = "company"
    PROFESSIONAL = "professional"

    @classmethod
    def from_string(cls, value: str):
        """
        Create an instance of the class from a string value.

        Args:
            value (str): The string representation of the class instance.

        Returns:
            cls: An instance of the class corresponding to the given string value.
        """
        return cls(value)
