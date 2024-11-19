from uuid import UUID

from fastapi import APIRouter, Body, Depends, File, Form, UploadFile
from fastapi import status as status_code
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.schemas.common import FilterParams, SearchParams
from app.schemas.job_application import JobSearchStatus
from app.schemas.professional import (
    PrivateMatches,
    ProfessionalResponse,
    ProfessionalUpdate,
    ProfessionalRequestBody,
)
from app.services import professional_service
from app.services.auth_service import get_current_company, get_current_professional
from app.sql_app.database import get_db
from app.sql_app.professional.professional_status import ProfessionalStatus
from app.utils.process_request import process_request

router = APIRouter()


@router.post(
    "/",
    description="Create a profile for a Professional.",
)
def create(
    professional: ProfessionalRequestBody = Body(),
    # photo: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
) -> JSONResponse:
    def _create():
        return professional_service.create(
            professional_request=professional,
            # photo=photo,
            db=db,
        )

    return process_request(
        get_entities_fn=_create,
        status_code=status_code.HTTP_201_CREATED,
        not_found_err_msg="Professional could not be created",
    )


@router.put(
    "/{professional_id}",
    description="Update a profile for a Professional.",
)
def update(
    professional_id: UUID,
    professional: ProfessionalRequestBody = Body(),
    private_matches: PrivateMatches = Form(),
    # photo: UploadFile | None = File(None),
    user: ProfessionalResponse = Depends(get_current_professional),
    db: Session = Depends(get_db),
) -> JSONResponse:
    def _update():
        return professional_service.update(
            professional_id=professional_id,
            professional=professional,
            private_matches=private_matches,
            db=db,
            # photo=photo,
        )

    return process_request(
        get_entities_fn=_update,
        status_code=status_code.HTTP_200_OK,
        not_found_err_msg="Professional could not be updated",
    )


@router.get(
    "/",
    description="Retreive all Professional profiles.",
)
def get_all(
    filter_params: FilterParams = Depends(),
    seacrh_params: SearchParams = Depends(),
    user: ProfessionalResponse = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> JSONResponse:
    def _get_all():
        return professional_service.get_all(
            db=db, filter_params=filter_params, seacrh_params=seacrh_params
        )

    return process_request(
        get_entities_fn=_get_all,
        status_code=status_code.HTTP_200_OK,
        not_found_err_msg="Could not fetch Professionals",
    )


@router.get(
    "/{professional_id}",
    description="Retreive a Professional profile by its ID.",
)
def get_by_id(
    professional_id: UUID,
    user: ProfessionalResponse = Depends(get_current_professional),
    db: Session = Depends(get_db),
) -> JSONResponse:
    def _get_by_id():
        return professional_service.get_by_id(professional_id=professional_id, db=db)

    return process_request(
        get_entities_fn=_get_by_id,
        status_code=status_code.HTTP_200_OK,
        not_found_err_msg="Could not fetch Professional",
    )


@router.get(
    "/{professional_id}/job-applications",
    description="View Job Applications by a Professional",
)
def get_applications(
    professional_id: UUID,
    filter_params: FilterParams = Depends(),
    user: ProfessionalResponse = Depends(get_current_professional),
    application_status: JobSearchStatus = Form(
        description="Status of the Job Application"
    ),
    db: Session = Depends(get_db),
):
    def _get_applications():
        return professional_service.get_applications(
            professional_id=professional_id,
            application_status=application_status,
            filter_params=filter_params,
            db=db,
        )

    return process_request(
        get_entities_fn=_get_applications,
        status_code=status_code.HTTP_200_OK,
        not_found_err_msg=f"Could not fetch Job Applications for professional with id {professional_id}",
    )
