from app.schemas.category import CategoryResponse
from app.services.external_db_service_urls import CATEGORIES_URL
from app.utils.request_handlers import perform_get_request


def get_all() -> list[CategoryResponse]:
    """
    Fetches all categories from the specified URL and returns them as a list of CategoryResponse objects.

    Returns:
        list[CategoryResponse]: A list of CategoryResponse objects representing the categories.
    """
    categories = perform_get_request(url=CATEGORIES_URL)
    return [CategoryResponse(**category) for category in categories]
