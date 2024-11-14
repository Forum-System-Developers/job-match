from enum import Enum


class JobStatus(Enum):
    """
    Enum representing different statuses applying to Job Ad or Job Application.

    Attributes:
        ACTIVE (str): The Job application or Ad is visible in searches by the Company.
        HIDDEN (str): The Job application or Ad is not visible for anyone but the creator.
        PRIVATE (str): The Job application or Ad can be viewed by id, but do not appear in searches.
        MATCHED (str): The Job application or Ad is matched by a Company.

    Methods:
        from_string(value: str) -> 'JobStatus':
            Converts a string to a JobStatus enum member.
    """

    ACTIVE = "active"
    HIDDEN = "hidden"
    PRIVATE = "private"
    MATCHED = "matched"

    @classmethod
    def from_string(cls, value: str) -> "JobStatus":
        """
        Create an instance of JobStatus from a string.

        Args:
            value (str): The string representation of the status.

        Returns:
            JobStatus: An instance of the JobStatus class.
        """
        return cls(value)
