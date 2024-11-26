from sqlalchemy.orm import Session

from app.schemas.category import CategoryResponse
from app.sql_app.category.category import Category


def get_all(db: Session) -> list[CategoryResponse]:
    categories = db.query(Category).all()
    return [CategoryResponse.create(category) for category in categories]
