from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.services import category_service
from app.utils.processors import process_request

router = APIRouter()


@router.get(
    "/",
    description="Retrieve all categories.",
)
def get_all_categories() -> JSONResponse:
    def _get_all_categories():
        return category_service.get_all()

    return process_request(
        get_entities_fn=_get_all_categories,
        status_code=status.HTTP_200_OK,
        not_found_err_msg="No categories found",
    )
