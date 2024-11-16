import logging

from sqlalchemy.orm import Session

from app.sql_app.city.city import City

logger = logging.getLogger(__name__)


def get_by_name(name: str, db: Session) -> City | None:
    """
    Retrieves an instance of the City model or None.

    Args:
        name (str): The Name of the City.
        db (Session): The database dependency.

    Returns:
        City | None: SQLAlchemy model for City.
    """
    return db.query(City).filter(City.name == name).first()
