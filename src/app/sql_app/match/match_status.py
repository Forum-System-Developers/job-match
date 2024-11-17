from enum import Enum


class MatchStatus(Enum):
    """
    MatchStatus is an enumeration representing the status of a match.

    Attributes:
        REQUESTED (str): The match has been requested.
        ACCEPTED (str): The match has been accepted.
        REJECTED (str): The match has been rejected.

    Methods:
        from_string(value: str) -> MatchStatus:
    """

    REQUESTED = "requested"
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
