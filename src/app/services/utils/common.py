from uuid import UUID

from fastapi import HTTPException

from app.schemas.company import CompanyResponse
from app.schemas.job_application import JobApplicationResponse
from app.schemas.professional import ProfessionalResponse
from app.utils.request_handlers import perform_get_request
from tests.services.urls import (
    COMPANY_BY_EMAIL_URL,
    COMPANY_BY_PHONE_NUMBER_URL,
    COMPANY_BY_USERNAME_URL,
    JOB_APPLICATIONS_BY_ID_URL,
    PROFESSIONAL_BY_EMAIL_URL,
    PROFESSIONAL_BY_USERNAME_URL,
)


def get_company_by_username(username: str) -> CompanyResponse | None:
    try:
        company = perform_get_request(
            url=COMPANY_BY_USERNAME_URL.format(username=username)
        )
        return CompanyResponse(**company)
    except HTTPException:
        return None


def get_company_by_email(email: str) -> CompanyResponse | None:
    try:
        company = perform_get_request(url=COMPANY_BY_EMAIL_URL.format(email=email))
        return CompanyResponse(**company)
    except HTTPException:
        return None


def get_company_by_phone_number(phone_number: str) -> CompanyResponse | None:
    try:
        company = perform_get_request(
            url=COMPANY_BY_PHONE_NUMBER_URL.format(phone_number=phone_number)
        )
        return CompanyResponse(**company)
    except HTTPException:
        return None


def get_professional_by_username(username: str) -> ProfessionalResponse | None:
    try:
        professional = perform_get_request(
            url=PROFESSIONAL_BY_USERNAME_URL.format(username=username)
        )
        return ProfessionalResponse(**professional)
    except HTTPException:
        return None


def get_professional_by_email(email: str) -> ProfessionalResponse | None:
    try:
        professional = perform_get_request(
            url=PROFESSIONAL_BY_EMAIL_URL.format(email=email)
        )
        return ProfessionalResponse(**professional)
    except HTTPException:
        return None


def get_job_application_by_id(
    job_application_id: UUID,
) -> JobApplicationResponse | None:
    try:
        job_application = perform_get_request(
            url=JOB_APPLICATIONS_BY_ID_URL.format(job_application_id=job_application_id)
        )
        return JobApplicationResponse(**job_application)
    except HTTPException:
        return None
