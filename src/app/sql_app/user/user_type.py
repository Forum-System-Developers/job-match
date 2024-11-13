from enum import Enum


class UserType(Enum):
    """
    UserType is an enumeration that represents different types of users.

    Attributes:
        professional (str): Represents a professional user.
        employer (str): Represents an employer user.
    """

    PROFESSIONAL = "professional"
    EMPLOYER = "employer"

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
