import logging
from typing import Any, Callable, Union

from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

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


def process_db_transaction(transaction_func: Callable, db: Session) -> Any:
    """
    Executes a database transaction function and handles exceptions.

    Args:
        transaction_func (Callable): The function to execute within the transaction.
        db (Session): The SQLAlchemy database session.

    Returns:
        Any: The result of the transaction function if successful.

    Raises:
        ApplicationError: If an IntegrityError or SQLAlchemyError occurs during the transaction.
    """
    try:
        return transaction_func()
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error: {str(e)}")
        raise ApplicationError(
            detail="Database conflict occurred", status_code=status.HTTP_409_CONFLICT
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Unexpected DB error: {str(e)}")
        raise ApplicationError(
            detail="Internal server error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def _format_response(data: Union[BaseModel, list[BaseModel]]) -> dict:
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
