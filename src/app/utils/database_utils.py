import logging
from typing import Any, Callable

from fastapi import status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.exceptions.custom_exceptions import ApplicationError

logger = logging.getLogger(__name__)


def handle_database_operation(db_request: Callable, db: Session) -> Any:
    try:
        return db_request()
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
