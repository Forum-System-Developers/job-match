from enum import Enum


class SkillLevel(Enum):
    """
    SkillLevel is an enumeration representing different levels of skill proficiency.

    Attributes:
        INTERN (str): Represents an intern level skill.
        INTERMEDIATE (str): Represents an intermediate level skill.
        ADVANCED (str): Represents an advanced level skill.
        EXPERT (str): Represents an expert level skill.
    """

    INTERN = "intern"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

    @classmethod
    def from_string(cls, value: str) -> "SkillLevel":
        """
        Convert a string to a SkillLevel instance.

        Args:
            value (str): The string representation of the SkillLevel.

        Returns:
            SkillLevel: An instance of SkillLevel corresponding to the given string.
        """
        return cls(value)
