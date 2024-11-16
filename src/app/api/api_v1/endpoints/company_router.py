from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.company import CompanyResponse
from app.services import company_service
from src.app.sql_app.database import get_db
from src.app.utils.process_request import process_request

router = APIRouter()


@router.get(
    "/",
    response_model=list[CompanyResponse],
    description="Retrieve all companies.",
)
def get_all_companies(
    skip: int = 0, limit: int = 50, db: Session = Depends(get_db)
) -> list[CompanyResponse]:
    def _get_all_companies():
        return company_service.get_all(db=db, skip=skip, limit=limit)

    return process_request(
        get_entities_fn=_get_all_companies,
        not_found_err_msg="No companies found",
    )


@router.get(
    "/{id}",
    description="Retrieve a company by its unique identifier.",
)
def get_company_by_id(id: UUID, db: Session = Depends(get_db)) -> CompanyResponse:
    def _get_company_by_id():
        return company_service.get_by_id(id=id, db=db)

    return process_request(
        get_entities_fn=_get_company_by_id,
        not_found_err_msg=f"Company with id {id} not found",
    )
