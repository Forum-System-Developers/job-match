from enum import Enum


class JobAdStatus(Enum):
    """
    An enumeration representing the status of a job advertisement.

    Attributes:
        ACTIVE (str): Represents an active job advertisement.
        ARCHIVED (str): Represents an archived job advertisement.
    """

    ACTIVE = "active"
    ARCHIVED = "archived"

    @classmethod
    def from_string(cls, value: str) -> "JobAdStatus":
        """
        Create a JobAdStatus instance from a string.

        Args:
            value (str): The string representation of the JobAdStatus.

        Returns:
            JobAdStatus: An instance of JobAdStatus corresponding to the given string.
        """
        return cls(value)
