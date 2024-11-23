from typing import Union
from uuid import UUID

from fastapi import APIRouter, Body, Depends, File, Form, Query, UploadFile
from fastapi import status as status_code
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.schemas.common import FilterParams, SearchParams
from app.schemas.job_application import JobSearchStatus
from app.schemas.professional import (
    PrivateMatches,
    ProfessionalRequestBody,
    ProfessionalUpdateRequestBody,
)
from app.services import professional_service
from app.services.auth_service import get_current_user, require_professional_role
from app.sql_app.database import get_db
from app.utils.process_request import process_request

router = APIRouter()


@router.post(
    "/",
    description="Create a profile for a Professional.",
)
def create(
    professional_request: ProfessionalRequestBody = Body(),
    db: Session = Depends(get_db),
) -> JSONResponse:
    def _create():
        return professional_service.create(
            professional_request=professional_request,
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
    dependencies=[Depends(require_professional_role)],
)
def update(
    professional_id: UUID,
    professional: ProfessionalUpdateRequestBody = Body(),
    db: Session = Depends(get_db),
) -> JSONResponse:
    def _update():
        return professional_service.update(
            professional_id=professional_id,
            professional_request=professional,
            db=db,
        )

    return process_request(
        get_entities_fn=_update,
        status_code=status_code.HTTP_200_OK,
        not_found_err_msg="Professional could not be updated",
    )


@router.patch(
    "/{professional_id}/private-matches",
    description="Set matches to Private or Public",
    dependencies=[Depends(require_professional_role)],
)
def private_matches(
    professional_id: UUID,
    private_matches: PrivateMatches = Form(),
    db: Session = Depends(get_db),
) -> JSONResponse:
    def _private_matches():
        return professional_service.set_matches_status(
            professional_id=professional_id, db=db, private_matches=private_matches
        )

    return process_request(
        get_entities_fn=_private_matches,
        status_code=status_code.HTTP_200_OK,
        not_found_err_msg="An error ocurred while setting matches status",
    )


@router.post(
    "/{professional_id}/upload-photo",
    description="Upload a photo",
    dependencies=[Depends(require_professional_role)],
)
def upload(
    professional_id: UUID,
    photo: UploadFile = File(),
    db: Session = Depends(get_db),
) -> JSONResponse:
    def _upload():
        return professional_service.upload(
            professional_id=professional_id,
            photo=photo,
            db=db,
        )

    return process_request(
        get_entities_fn=_upload,
        status_code=status_code.HTTP_200_OK,
        not_found_err_msg="Could not upload photo",
    )


@router.get(
    "/{professional_id}/download-photo",
    response_model=None,
    dependencies=[Depends(get_current_user)],
)
def download(
    professional_id: UUID, db: Session = Depends(get_db)
) -> Union[StreamingResponse, JSONResponse]:
    return professional_service.download(professional_id=professional_id, db=db)


@router.post(
    "/all",
    description="Retreive all Professional profiles.",
    dependencies=[Depends(get_current_user)],
)
def get_all(
    filter_params: FilterParams = Depends(),
    search_params: SearchParams = Depends(),
    db: Session = Depends(get_db),
) -> JSONResponse:
    def _get_all():
        return professional_service.get_all(
            db=db, filter_params=filter_params, search_params=search_params
        )

    return process_request(
        get_entities_fn=_get_all,
        status_code=status_code.HTTP_200_OK,
        not_found_err_msg="Could not fetch Professionals",
    )


@router.get(
    "/{professional_id}",
    description="Retreive a Professional profile by its ID.",
    dependencies=[Depends(get_current_user)],
)
def get_by_id(
    professional_id: UUID,
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
    dependencies=[Depends(get_current_user)],
)
def get_applications(
    professional_id: UUID,
    filter_params: FilterParams = Depends(),
    application_status: JobSearchStatus = Query(
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
