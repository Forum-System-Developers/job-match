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
    Custom exception class for application errors.

    Attributes:
        data (ExceptionData): An instance of ExceptionData containing details about the error.

    Args:
        data (ExceptionData): The data associated with the exception.
    """

    def __init__(self, data: ExceptionData):
        self.data = data

    def __str__(self):
        return f"Error {self.data.status}: {self.data.detail}"
