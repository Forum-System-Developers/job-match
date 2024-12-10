import logging
from uuid import UUID

from fastapi import HTTPException

from app.schemas.company import CompanyResponse
from app.schemas.job_ad import JobAdResponse
from app.schemas.job_application import JobApplicationResponse
from app.schemas.match import MatchResponse
from app.schemas.professional import ProfessionalResponse
from app.schemas.skill import SkillResponse
from app.services.external_db_service_urls import (
    COMPANY_BY_EMAIL_URL,
    COMPANY_BY_PHONE_NUMBER_URL,
    COMPANY_BY_USERNAME_URL,
    JOB_AD_BY_ID_URL,
    JOB_APPLICATIONS_BY_ID_URL,
    MATCH_REQUESTS_BY_ID_URL,
    PROFESSIONAL_BY_EMAIL_URL,
    PROFESSIONAL_BY_USERNAME_URL,
    PROFESSIONALS_BY_ID_URL,
    SKILLS_URL,
)
from app.utils.request_handlers import perform_get_request

logger = logging.getLogger(__name__)


def get_company_by_username(username: str) -> CompanyResponse | None:
    try:
        company = perform_get_request(
            url=COMPANY_BY_USERNAME_URL.format(username=username)
        )
        logger.info(f"Retrieved company with username {username}")
        return CompanyResponse(**company)
    except HTTPException:
        return None


def get_company_by_email(email: str) -> CompanyResponse | None:
    try:
        company = perform_get_request(url=COMPANY_BY_EMAIL_URL.format(email=email))
        logger.info(f"Retrieved company with email {email}")
        return CompanyResponse(**company)
    except HTTPException:
        return None


def get_company_by_phone_number(phone_number: str) -> CompanyResponse | None:
    try:
        company = perform_get_request(
            url=COMPANY_BY_PHONE_NUMBER_URL.format(phone_number=phone_number)
        )
        logger.info(f"Retrieved company with phone number {phone_number}")
        return CompanyResponse(**company)
    except HTTPException:
        return None


def get_professional_by_id(professional_id: UUID) -> ProfessionalResponse | None:
    try:
        professional = perform_get_request(
            url=PROFESSIONALS_BY_ID_URL.format(professional_id=professional_id)
        )
        logger.info(f"Retrieved professional with id {professional_id}")
        return ProfessionalResponse(**professional)
    except HTTPException:
        return None


def get_professional_by_username(username: str) -> ProfessionalResponse | None:
    try:
        professional = perform_get_request(
            url=PROFESSIONAL_BY_USERNAME_URL.format(username=username)
        )
        logger.info(f"Retrieved professional with username {username}")
        return ProfessionalResponse(**professional)
    except HTTPException:
        return None


def get_professional_by_email(email: str) -> ProfessionalResponse | None:
    try:
        professional = perform_get_request(
            url=PROFESSIONAL_BY_EMAIL_URL.format(email=email)
        )
        logger.info(f"Retrieved professional with email {email}")
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
        logger.info(f"Retrieved job application with id {job_application_id}")
        return JobApplicationResponse(**job_application)
    except HTTPException:
        return None


def get_job_ad_by_id(job_ad_id: UUID) -> JobAdResponse | None:
    try:
        job_ad = perform_get_request(url=JOB_AD_BY_ID_URL.format(job_ad_id=job_ad_id))
        logger.info(f"Retrieved job ad with id {job_ad_id}")
        return JobAdResponse(**job_ad)
    except HTTPException:
        return None


def get_match_request_by_id(
    job_ad_id: UUID,
    job_application_id: UUID,
) -> MatchResponse | None:
    try:
        match = perform_get_request(
            url=MATCH_REQUESTS_BY_ID_URL.format(
                job_ad_id=job_ad_id,
                job_application_id=job_application_id,
            )
        )
        logger.info(
            f"Retrieved match request for job ad with id {job_ad_id} and job application with id {job_application_id}"
        )
        return MatchResponse(**match)
    except HTTPException:
        return None


def get_skill_by_id(skill_id: UUID) -> SkillResponse | None:
    try:
        skill = perform_get_request(url=SKILLS_URL.format(skill_id=skill_id))
        logger.info(f"Retrieved skill with id {skill_id}")
        return SkillResponse(**skill)
    except HTTPException:
        return None
