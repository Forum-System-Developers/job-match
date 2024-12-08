from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.schemas.common import FilterParams, JobAdSearchParams
from app.schemas.company import CompanyResponse
from app.schemas.job_ad import JobAdCreate, JobAdUpdate
from app.services import job_ad_service, match_service
from app.services.auth_service import get_current_user, require_company_role
from app.utils.processors import process_request

router = APIRouter()


@router.post(
    "/all",
    description="Retrieve all job advertisements.",
    dependencies=[Depends(get_current_user)],
)
def get_all_job_ads(
    search_params: JobAdSearchParams,
    filter_params: FilterParams = Depends(),
) -> JSONResponse:
    def _get_all_job_ads():
        return job_ad_service.get_all(
            filter_params=filter_params, search_params=search_params
        )

    return process_request(
        get_entities_fn=_get_all_job_ads,
        status_code=status.HTTP_200_OK,
        not_found_err_msg="No job ads found",
    )


@router.get(
    "/{job_ad_id}",
    description="Retrieve a job advertisement by its unique identifier.",
    dependencies=[Depends(get_current_user)],
)
def get_job_ad_by_id(job_ad_id: UUID) -> JSONResponse:
    def _get_job_ad_by_id():
        return job_ad_service.get_by_id(job_ad_id=job_ad_id)

    return process_request(
        get_entities_fn=_get_job_ad_by_id,
        status_code=status.HTTP_200_OK,
        not_found_err_msg=f"Job Ad with id {job_ad_id} not found",
    )


@router.post(
    "/",
    description="Create a new job advertisement.",
)
def create_job_ad(
    job_ad_data: JobAdCreate,
    company: CompanyResponse = Depends(require_company_role),
) -> JSONResponse:
    def _create_job_ad():
        return job_ad_service.create(
            job_ad_data=job_ad_data, company_id=company.id
        )

    return process_request(
        get_entities_fn=_create_job_ad,
        status_code=status.HTTP_201_CREATED,
        not_found_err_msg="Job Ad not created",
    )


@router.put(
    "/{job_ad_id}",
    description="Update a job advertisement by its unique identifier.",
    dependencies=[Depends(require_company_role)],
)
def update_job_ad(
    job_ad_id: UUID,
    job_ad_data: JobAdUpdate,
) -> JSONResponse:
    def _update_job_ad():
        return job_ad_service.update(
            job_ad_id=job_ad_id, job_ad_data=job_ad_data
        )

    return process_request(
        get_entities_fn=_update_job_ad,
        status_code=status.HTTP_200_OK,
        not_found_err_msg=f"Job Ad with id {job_ad_id} not found",
    )


@router.post(
    "/{job_ad_id}/skills/{skill_id}",
    description="Add a skill requirement to a job advertisement.",
    dependencies=[Depends(require_company_role)],
)
def add_job_ad_skill(
    job_ad_id: UUID,
    skill_id: UUID,
) -> JSONResponse:
    def _add_job_ad_skill():
        return job_ad_service.add_skill_requirement(
            job_ad_id=job_ad_id,
            skill_id=skill_id,
        )

    return process_request(
        get_entities_fn=_add_job_ad_skill,
        status_code=status.HTTP_200_OK,
        not_found_err_msg=f"Job Ad with id {job_ad_id} not found",
    )


@router.get(
    "/{job_ad_id}/match-requests",
    description="Retrieve all match requests for a job advertisement.",
)
def view_received_match_requests(
    job_ad_id: UUID,
    company: CompanyResponse = Depends(require_company_role),
) -> JSONResponse:
    def _get_job_ad_requests():
        return match_service.view_received_job_application_match_requests(
            job_ad_id=job_ad_id,
            company_id=company.id,
        )

    return process_request(
        get_entities_fn=_get_job_ad_requests,
        status_code=status.HTTP_200_OK,
        not_found_err_msg=f"No requests found for job ad with id {job_ad_id}",
    )


@router.patch(
    "/{job_ad_id}/job-applications/{job_application_id}/match-requests",
    description="Accept a match request for a job advertisement.",
)
def accept_match_request(
    job_ad_id: UUID,
    job_application_id: UUID,
    company: CompanyResponse = Depends(require_company_role),
) -> JSONResponse:
    def _accept_job_ad_request():
        return match_service.accept_job_application_match_request(
            job_ad_id=job_ad_id,
            job_application_id=job_application_id,
            company_id=company.id,
        )

    return process_request(
        get_entities_fn=_accept_job_ad_request,
        status_code=status.HTTP_200_OK,
        not_found_err_msg=f"Match request not found for job ad with id {job_ad_id}",
    )


@router.post(
    "/{job_ad_id}/job-applications/{job_application_id}/match-requests",
    description="Send a match request to a job application.",
)
def send_match_request(
    job_ad_id: UUID,
    job_application_id: UUID,
    company: CompanyResponse = Depends(require_company_role),
) -> JSONResponse:
    def _send_job_ad_request():
        return match_service.send_job_application_match_request(
            job_ad_id=job_ad_id,
            job_application_id=job_application_id,
            company_id=company.id,
        )

    return process_request(
        get_entities_fn=_send_job_ad_request,
        status_code=status.HTTP_200_OK,
        not_found_err_msg=f"Match request not sent for job ad with id {job_ad_id}",
    )


@router.get(
    "/{job_ad_id}/sent-match-requests",
    description="Retrieve all sent match requests for a job advertisement.",
)
def view_sent_match_requests(
    job_ad_id: UUID,
    company: CompanyResponse = Depends(require_company_role),
) -> JSONResponse:
    def _view_sent_requests():
        return match_service.view_sent_job_application_match_requests(
            job_ad_id=job_ad_id,
            company_id=company.id,
        )

    return process_request(
        get_entities_fn=_view_sent_requests,
        status_code=status.HTTP_200_OK,
        not_found_err_msg=f"No requests found for job ad with id {job_ad_id}",
    )
