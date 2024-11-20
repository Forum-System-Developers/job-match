from enum import Enum


class MatchStatus(Enum):
    """
    MatchStatus is an enumeration representing the status of a match.

    Attributes:
        REQUESTED (str): DEPRECATED - use REQUESTED_BY_JOB_APP or REQUESTED_BY_JOB_AD instead.
        REQUESTED_BY_JOB_AD (str): The match was requested by a job advertisement.
        REQUESTED_BY_JOB_APP (str): The match was requested by a job application.
        ACCEPTED (str): The match has been accepted.
        REJECTED (str): The match has been rejected.

    Methods:
        from_string(value: str) -> MatchStatus:
    """
    REQUESTED = "requested"
    REQUESTED_BY_JOB_AD = "requested_by_job_ad"
    REQUESTED_BY_JOB_APP = "requested_by_job_application"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

    @classmethod
    def from_string(cls, value: str) -> "MatchStatus":
        """
        Create a MatchStatus instance from a string.

        Args:
            value (str): The string representation of the MatchStatus.

        Returns:
            MatchStatus: An instance of MatchStatus corresponding to the given string.
        """
        return cls(value)
