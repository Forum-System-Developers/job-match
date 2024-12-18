from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import JSONResponse, StreamingResponse

from app.schemas.common import FilterParams
from app.schemas.company import CompanyCreate, CompanyResponse, CompanyUpdate
from app.services import company_service, match_service
from app.services.auth_service import get_current_user, require_company_role
from app.utils.processors import process_request

router = APIRouter()


@router.get(
    "/",
    description="Retrieve all companies.",
)
def get_all_companies(filter_params: FilterParams = Depends()) -> JSONResponse:
    def _get_all_companies():
        return company_service.get_all(filter_params=filter_params)

    return process_request(
        get_entities_fn=_get_all_companies,
        status_code=status.HTTP_200_OK,
        not_found_err_msg="No companies found",
    )


@router.get(
    "/match-requests",
    description="Retrieve all match requests for the current company.",
)
def view_match_requests(
    filter_params: FilterParams = Depends(),
    company: CompanyResponse = Depends(require_company_role),
) -> JSONResponse:
    def _view_match_requests():
        return match_service.get_company_match_requests(
            company_id=company.id,
            filter_params=filter_params,
        )

    return process_request(
        get_entities_fn=_view_match_requests,
        status_code=status.HTTP_200_OK,
        not_found_err_msg="No match requests found",
    )


@router.get(
    "/{company_id}",
    description="Retrieve a company by its unique identifier.",
)
def get_company_by_id(company_id: UUID) -> JSONResponse:
    def _get_company_by_id():
        return company_service.get_by_id(company_id=company_id)

    return process_request(
        get_entities_fn=_get_company_by_id,
        status_code=status.HTTP_200_OK,
        not_found_err_msg=f"Company with id {company_id} not found",
    )


@router.post(
    "/",
    description="Create a new company.",
)
def create_company(company_data: CompanyCreate) -> JSONResponse:
    def _create_company():
        return company_service.create(company_data=company_data)

    return process_request(
        get_entities_fn=_create_company,
        status_code=status.HTTP_201_CREATED,
        not_found_err_msg="Company not created",
    )


@router.put(
    "/",
    description="Update the current company.",
)
def update_company(
    company_data: CompanyUpdate,
    company: CompanyResponse = Depends(require_company_role),
) -> JSONResponse:
    def _update_company():
        return company_service.update(company_id=company.id, company_data=company_data)

    return process_request(
        get_entities_fn=_update_company,
        status_code=status.HTTP_200_OK,
        not_found_err_msg=f"Company with id {company.id} not updated",
    )


@router.post(
    "/upload-logo",
    description="Upload a logo for the current company.",
)
def upload_logo(
    logo: UploadFile = File(),
    company: CompanyResponse = Depends(require_company_role),
) -> JSONResponse:
    def _upload_logo():
        return company_service.upload_logo(company_id=company.id, logo=logo)

    return process_request(
        get_entities_fn=_upload_logo,
        status_code=status.HTTP_200_OK,
        not_found_err_msg="Could not upload logo",
    )


@router.get(
    "/{company_id}/download-logo",
    description="Download the logo of the current company",
    dependencies=[Depends(get_current_user)],
)
def download_logo(
    company_id: UUID,
) -> StreamingResponse:
    return company_service.download_logo(company_id=company_id)


@router.delete(
    "/delete-logo",
    description="Delete the logo of the current company.",
)
def delete_logo(
    company: CompanyResponse = Depends(require_company_role),
) -> JSONResponse:
    def _delete_logo():
        return company_service.delete_logo(company_id=company.id)

    return process_request(
        get_entities_fn=_delete_logo,
        status_code=status.HTTP_200_OK,
        not_found_err_msg="Could not delete logo",
    )
