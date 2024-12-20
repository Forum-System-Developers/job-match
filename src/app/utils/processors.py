import logging
from typing import Any, Callable, Union

from fastapi import status
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel

from app.exceptions.custom_exceptions import ApplicationError

logger = logging.getLogger(__name__)


def process_request(
    get_entities_fn: Callable,
    status_code: int,
    not_found_err_msg: str,
) -> JSONResponse:
    """
    Processes a request by calling the provided function and handling exceptions.

    Args:
        get_entities_fn (Callable): A function that retrieves entities.
        status_code (int): The status code to return on successful processing.
        not_found_err_msg (str): The error message to log if a TypeError occurs.

    Returns:
        JSONResponse: A JSON response with the appropriate status code and content.

    Raises:
        ApplicationError: If an application-specific error occurs.
        TypeError: If a type error occurs.
        SyntaxError: If a syntax error occurs.
    """
    try:
        response = get_entities_fn()
        return JSONResponse(status_code=status_code, content=_format_response(response))
    except ApplicationError as ex:
        logger.exception(str(ex))
        return JSONResponse(
            status_code=ex.data.status,
            content={"detail": {"error": ex.data.detail}},
        )
    except TypeError as ex:
        logger.exception(not_found_err_msg)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": {"error": str(ex)}},
        )
    except SyntaxError as ex:
        logger.exception("Pers thrown an exception")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": {"error": str(ex)}},
        )


async def process_async_request(
    get_entities_fn: Callable,
    status_code: int,
    not_found_err_msg: str,
) -> JSONResponse | RedirectResponse:
    """
    Asynchronously processes a request by calling the provided function to get entities and returns an appropriate response.

    Args:
        get_entities_fn (Callable): A function that retrieves entities asynchronously.
        status_code (int): The HTTP status code to return in the response if successful.
        not_found_err_msg (str): The error message to log if a TypeError occurs.

    Returns:
        JSONResponse | RedirectResponse: A JSON response with the formatted data or a redirect response.

    Raises:
        ApplicationError: If an application-specific error occurs.
        TypeError: If a type error occurs, typically indicating a not found error.
        SyntaxError: If a syntax error occurs, typically indicating a bad request.
    """
    try:
        response = await get_entities_fn()

        if isinstance(response, RedirectResponse):
            return response

        formatted_response = _format_response(response)

        return JSONResponse(status_code=status_code, content=formatted_response)
    except ApplicationError as ex:
        logger.exception(str(ex))
        return JSONResponse(
            status_code=ex.data.status,
            content={"detail": {"error": ex.data.detail}},
        )
    except TypeError as ex:
        logger.exception(not_found_err_msg)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": {"error": str(ex)}},
        )
    except SyntaxError as ex:
        logger.exception("Pers thrown an exception")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": {"error": str(ex)}},
        )


def _format_response(
    data: BaseModel | list[BaseModel],
) -> dict[str, Any] | list[dict[str, Any]]:
    """
    Formats the response data to include the detail key.

    Args:
        data (Union[BaseModel, list[BaseModel]]): The data to format.

    Returns:
        dict: The formatted response data.
    """
    if isinstance(data, list):
        return {"detail": [item.model_dump(mode="json") for item in data]}
    return {
        "detail": data.model_dump(mode="json") if isinstance(data, BaseModel) else data
    }
