from sqlalchemy.orm import Session

from app.schemas.category import CategoryResponse
from app.sql_app.category.category import Category


def get_all(db: Session) -> list[CategoryResponse]:
    """
    Retrieve all categories from the database.

    Args:
        db (Session): The database session used to query the categories.

    Returns:
        list[CategoryResponse]: A list of CategoryResponse objects representing all categories in the database.
    """
    categories = db.query(Category).all()
    return [CategoryResponse.create(category) for category in categories]
