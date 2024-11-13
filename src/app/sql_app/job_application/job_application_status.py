from enum import Enum


class JobApplicationStatus(Enum):
    """
    Enum representing different access levels.

    Attributes:
        ACTIVE (str): The Job application is visible in searches by the Company.
        HIDDEN (str): The Job application is not visible for anyone but the creator.
        PRIVATE (str): The Job application can be viewed by id, but do not appear in searches.
        MATCHED (str): The Job application is matched by a Company.

    Methods:
        from_string(value: str) -> 'JobApplicationStatus':
            Converts a string to a JobApplicationStatus enum member.
    """

    ACTIVE = "active"
    HIDDEN = "hidden"
    PRIVATE = "private"
    MATCHED = "matched"

    @classmethod
    def from_string(cls, value: str) -> "JobApplicationStatus":
        """
        Create an instance of JobApplicationStatus from a string.

        Args:
            value (str): The string representation of the status.

        Returns:
            JobApplicationStatus: An instance of the JobApplicationStatus class.
        """
        return cls(value)
