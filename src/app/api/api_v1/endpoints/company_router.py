from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.schemas.common import FilterParams
from app.schemas.company import CompanyCreate, CompanyResponse, CompanyUpdate
from app.services import company_service
from app.services.auth_service import get_current_company
from app.sql_app.database import get_db
from app.utils.process_request import process_request

router = APIRouter()


@router.get(
    "/",
    description="Retrieve all companies.",
)
def get_all_companies(
    filter_params: FilterParams = Depends(), db: Session = Depends(get_db)
) -> JSONResponse:
    def _get_all_companies():
        return company_service.get_all(db=db, filter_params=filter_params)

    return process_request(
        get_entities_fn=_get_all_companies,
        status_code=status.HTTP_200_OK,
        not_found_err_msg="No companies found",
    )


@router.get(
    "/{id}",
    description="Retrieve a company by its unique identifier.",
)
def get_company_by_id(id: UUID, db: Session = Depends(get_db)) -> JSONResponse:
    def _get_company_by_id():
        return company_service.get_by_id(id=id, db=db)

    return process_request(
        get_entities_fn=_get_company_by_id,
        status_code=status.HTTP_200_OK,
        not_found_err_msg=f"Company with id {id} not found",
    )


@router.post(
    "/",
    description="Create a new company.",
)
def create_company(
    company_data: CompanyCreate,
    logo: UploadFile | None = File(None),
    db: Session = Depends(get_db),
) -> JSONResponse:
    def _create_company():
        return company_service.create(company_data=company_data, db=db, logo=logo)

    return process_request(
        get_entities_fn=_create_company,
        status_code=status.HTTP_201_CREATED,
        not_found_err_msg="Company not created",
    )


@router.put(
    "/{id}",
    description="Update a company by its unique identifier.",
)
def update_company(
    id: UUID,
    company_data: CompanyUpdate,
    company: CompanyResponse = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> JSONResponse:
    def _update_company():
        return company_service.update(id=id, company_data=company_data, db=db)

    return process_request(
        get_entities_fn=_update_company,
        status_code=status.HTTP_200_OK,
        not_found_err_msg=f"Company with id {id} not found",
    )
