from pydantic import BaseModel


class ExceptionData(BaseModel):
    """
    ExceptionData is a model that represents the structure of exception details.

    Attributes:
        detail (str): A string containing the detail of the exception.
        status (int): An integer representing the status code associated with the exception.
    """

    detail: str
    status: int


class ApplicationError(Exception):
    """
    ApplicationError is a custom exception class that includes detailed error information.

    Attributes:
        data (ExceptionData): An instance of ExceptionData containing the error details.
    """

    def __init__(self, detail: str, status_code: int):
        self.data = ExceptionData(detail=detail, status=status_code)

    def __str__(self):
        """
        Returns a string representation of the ApplicationError.

        Returns:
            str: A formatted string containing the status code and detail of the exception.
        """
        return f"Error {self.data.status}: {self.data.detail}"
