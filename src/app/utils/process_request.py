import logging
from typing import Callable, Union

from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.exceptions.custom_exceptions import ApplicationError

logger = logging.getLogger(__name__)


def format_response(data: Union[BaseModel, list[BaseModel]]) -> dict:
    """
    Formats the response data to include the detail key.

    Args:
        data (Union[BaseModel, list[BaseModel]]): The data to format.

    Returns:
        dict: The formatted response data.
    """
    if isinstance(data, list):
        return {"detail": [item.model_dump() for item in data]}
    return {"detail": data.model_dump()}


def process_request(
    get_entities_fn: Callable,
    status_code: int,
    not_found_err_msg: str,
) -> JSONResponse:
    try:
        response = get_entities_fn()
        return JSONResponse(status_code=status_code, content=format_response(response))
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
