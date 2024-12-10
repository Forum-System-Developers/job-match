from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.services import city_service
from app.utils.processors import process_request

router = APIRouter()


@router.get("/", description="Fetch all cities.")
def get_all() -> JSONResponse:
    def _get_all():
        return city_service.get_all()

    return process_request(
        get_entities_fn=_get_all,
        status_code=status.HTTP_201_CREATED,
        not_found_err_msg="Job Requirement not created",
    )
