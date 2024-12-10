from enum import Enum


class ProfessionalStatus(str, Enum):
    """
    ProfessionalStatus is an enumeration representing the status of a professional.

    Attributes:
        active (str): the only status that allows active applications.
        busy (str): job applications by the professional are not visible during.
    """

    ACTIVE = "active"
    BUSY = "busy"

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
