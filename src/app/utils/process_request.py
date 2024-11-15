from typing import Callable, Union

from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.app.exceptions.custom_exceptions import ApplicationError


def process_request(
    get_entities_fn: Callable,
    not_found_err_msg: str,
) -> Union[BaseModel, JSONResponse]:
    """
    Processes a request by calling the provided function and handling exceptions.

    Args:
        get_entities_fn (Callable): A function that retrieves entities.
        not_found_err_msg (str): Error message to log if a TypeError occurs.

    Returns:
        Union[BaseModel, JSONResponse]: The result of the function call if successful,
        or a JSONResponse with an appropriate error message and status code if an exception occurs.

    Raises:
        TypeError: If the provided function raises a TypeError.
        SyntaxError: If the provided function raises a SyntaxError.
    """
    try:
        return get_entities_fn()
    except ApplicationError as ex:
        return JSONResponse(
            status_code=ex.data.status,
            content={"detail": {"error": ex.data.detail}},
        )
    except TypeError as ex:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": {"error": str(ex)}},
        )
    except SyntaxError as ex:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": {"error": str(ex)}},
        )
