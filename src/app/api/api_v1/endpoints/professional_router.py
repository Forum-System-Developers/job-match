from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from fastapi import status as status_code
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.schemas.common import FilterParams, SearchParams
from app.schemas.job_application import JobSearchStatus
from app.schemas.professional import (
    PrivateMatches,
    ProfessionalCreate,
    ProfessionalResponse,
    ProfessionalUpdate,
)
from app.services import professional_service
from app.services.auth_service import (
    get_current_user,
    require_professional_role,
)
from app.sql_app.database import get_db
from app.utils.processors import process_request

router = APIRouter()


@router.post(
    "/",
    description="Create a profile for a Professional.",
)
def create(professional_data: ProfessionalCreate) -> JSONResponse:
    def _create():
        return professional_service.create(
            professional_data=professional_data,
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
    professional_update: ProfessionalUpdate,
) -> JSONResponse:
    def _update():
        return professional_service.update(
            professional_id=professional_id,
            professional_data=professional_update,
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
    "/upload-photo",
    description="Upload a photo",
)
def upload_photo(
    professional: ProfessionalResponse = Depends(require_professional_role),
    photo: UploadFile = File(),
) -> JSONResponse:
    def _upload():
        return professional_service.upload_photo(
            professional_id=professional.id,
            photo=photo,
        )

    return process_request(
        get_entities_fn=_upload,
        status_code=status_code.HTTP_200_OK,
        not_found_err_msg="Could not upload photo",
    )


@router.post("/upload-cv", description="Upload CV file")
def upload_cv(
    professional: ProfessionalResponse = Depends(require_professional_role),
    cv: UploadFile = File(),
) -> JSONResponse:
    def _upload():
        return professional_service.upload_cv(
            professional_id=professional.id,
            cv=cv,
        )

    return process_request(
        get_entities_fn=_upload,
        status_code=status_code.HTTP_200_OK,
        not_found_err_msg="Could not upload CV",
    )


@router.get(
    "/{professional_id}/download-photo",
    response_model=None,
    dependencies=[Depends(get_current_user)],
    status_code=status_code.HTTP_200_OK,
    description="Fetch a Photo of a Professional",
)
def download_photo(professional_id: UUID) -> StreamingResponse:
    return professional_service.download_photo(professional_id=professional_id)


@router.get(
    "/{professional_id}/download-cv",
    response_model=None,
    dependencies=[Depends(get_current_user)],
    status_code=status_code.HTTP_200_OK,
)
def download_cv(professional_id: UUID) -> StreamingResponse:
    return professional_service.download_cv(professional_id=professional_id)


@router.delete(
    "/cv",
    description="Delete the cv of a professional.",
)
def delete_cv(
    professional: ProfessionalResponse = Depends(require_professional_role),
) -> JSONResponse:
    def _delete_cv():
        return professional_service.delete_cv(
            professional_id=professional.id,
        )

    return process_request(
        get_entities_fn=_delete_cv,
        status_code=status_code.HTTP_200_OK,
        not_found_err_msg="Could not delete CV",
    )


@router.post(
    "/all",
    description="Retreive all Professional profiles.",
    dependencies=[Depends(get_current_user)],
)
def get_all(
    filter_params: FilterParams = Depends(),
    search_params: SearchParams = Depends(),
) -> JSONResponse:
    def _get_all():
        return professional_service.get_all(
            filter_params=filter_params, search_params=search_params
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
def get_by_id(professional_id: UUID) -> JSONResponse:
    def _get_by_id():
        return professional_service.get_by_id(professional_id=professional_id)

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
) -> JSONResponse:
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


@router.get(
    "/{professional_id}/skills",
    description="Fetch Skills for a professional",
    dependencies=[Depends(get_current_user)],
)
def get_skills(professional_id: UUID, db: Session = Depends(get_db)) -> JSONResponse:
    def _get_skills():
        return professional_service.get_skills(professional_id=professional_id, db=db)

    return process_request(
        get_entities_fn=_get_skills,
        status_code=status_code.HTTP_200_OK,
        not_found_err_msg="Skills for professional not found",
    )


@router.get(
    "/{professional_id}/match-requests",
    description="Fetch Match Requests for a professional",
    dependencies=[Depends(require_professional_role)],
)
def get_match_requests(
    professional_id: UUID, db: Session = Depends(get_db)
) -> JSONResponse:
    def _get_match_requests():
        return professional_service.get_match_requests(
            professional_id=professional_id, db=db
        )

    return process_request(
        get_entities_fn=_get_match_requests,
        status_code=status_code.HTTP_200_OK,
        not_found_err_msg="Skills for professional not found",
    )
