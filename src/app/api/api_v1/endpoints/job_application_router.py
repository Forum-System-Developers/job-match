from uuid import UUID

from fastapi import APIRouter, Body, Depends
from fastapi import status as status_code
from fastapi.responses import JSONResponse

from app.schemas.common import FilterParams, SearchJobApplication
from app.schemas.job_application import (
    JobApplicationCreate,
    JobApplicationUpdate,
    MatchResponseRequest,
)
from app.schemas.professional import ProfessionalResponse
from app.services import job_application_service
from app.services.auth_service import (
    get_current_user,
    require_company_role,
    require_professional_role,
)
from app.sql_app.database import get_db
from app.utils.processors import process_request

router = APIRouter()


@router.post(
    "/",
    description="Create a Job Application.",
)
def create(
    professional: ProfessionalResponse = Depends(require_professional_role),
    application_create: JobApplicationCreate = Body(
        description="Job Application creation form"
    ),
) -> JSONResponse:
    def _create():
        return job_application_service.create(
            professional_id=professional.id,
            job_application_data=application_create,
        )

    return process_request(
        get_entities_fn=_create,
        status_code=status_code.HTTP_201_CREATED,
        not_found_err_msg="Job application could not be created",
    )


@router.put(
    "/{job_application_id}",
    description="Update a Job Application.",
)
def update(
    job_application_id: UUID,
    professional=Depends(require_professional_role),
    application_update: JobApplicationUpdate = Body(
        description="Job Application update form"
    ),
) -> JSONResponse:
    def _update():
        return job_application_service.update(
            professional_id=professional.id,
            job_application_id=job_application_id,
            job_application_update=application_update,
        )

    return process_request(
        get_entities_fn=_update,
        status_code=status_code.HTTP_200_OK,
        not_found_err_msg="Job application could not be updated",
    )


@router.post(
    "/all",
    description="Get all Job applications (filtered by indicated parameters)",
    dependencies=[Depends(get_current_user)],
)
def get_all(
    filter_params: FilterParams = Depends(),
    search_params: SearchJobApplication = Depends()
) -> JSONResponse:
    def _get_all():
        return job_application_service.get_all(
            filter_params=filter_params,
            search_params=search_params,
        )

    return process_request(
        get_entities_fn=_get_all,
        status_code=status_code.HTTP_200_OK,
        not_found_err_msg="Could not fetch Job Applications",
    )


@router.get(
    "/{job_application_id}",
    description="Fetch a Job Application by its ID",
    dependencies=[Depends(get_current_user)],
)
def get_by_id(
    job_application_id: UUID,
) -> JSONResponse:
    def _get_by_id():
        return job_application_service.get_by_id(job_application_id=job_application_id)

    return process_request(
        get_entities_fn=_get_by_id,
        status_code=status_code.HTTP_200_OK,
        not_found_err_msg="Could not fetch Job Application",
    )


@router.post(
    "/{job_application_id}/job-ads/{job_ad_id}",
    description="Send match request to a Job Application",
    dependencies=[Depends(require_company_role)],
)
def request_match(
    job_application_id: UUID,
    job_ad_id: UUID,
) -> JSONResponse:
    def _request_match():
        return job_application_service.request_match(
            job_application_id=job_application_id, job_ad_id=job_ad_id
        )

    return process_request(
        get_entities_fn=_request_match,
        status_code=status_code.HTTP_201_CREATED,
        not_found_err_msg="Could not process match request",
    )


@router.put(
    "/{job_application_id}/{job_ad_id}/match-response",
    description="Accept or reject a Match request",
    dependencies=[Depends(require_professional_role)],
)
def handle_match_response(
    job_application_id: UUID,
    job_ad_id: UUID,
    accept_request: MatchResponseRequest,
) -> JSONResponse:
    def _handle_match_response():
        return job_application_service.handle_match_response(
            job_application_id=job_application_id,
            job_ad_id=job_ad_id,
            accept_request=accept_request,
        )

    return process_request(
        get_entities_fn=_handle_match_response,
        status_code=status_code.HTTP_200_OK,
        not_found_err_msg="Could not accept match request",
    )


@router.get(
    "/{job_application_id}/match-requests",
    description="View Match requests.",
    dependencies=[Depends(require_professional_role)],
)
def view_match_requests(
    job_application_id: UUID,
    filter_params: FilterParams = Depends(),
) -> JSONResponse:
    def _view_match_requests():
        return job_application_service.view_match_requests(
            job_application_id=job_application_id,
            filter_params=filter_params,
        )

    return process_request(
        get_entities_fn=_view_match_requests,
        status_code=status_code.HTTP_200_OK,
        not_found_err_msg="Could not fetch match requests",
    )
