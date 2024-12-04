import re
from urllib.parse import parse_qs, urlparse
from uuid import UUID

from fastapi import status
from pydantic import BaseModel, EmailStr, HttpUrl, field_validator

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.custom_types import PASSWORD_REGEX, Password, Username
from app.sql_app.company.company import Company


class CompanyBase(BaseModel):
    id: UUID
    name: str
    address_line: str
    city: str
    description: str
    email: EmailStr
    phone_number: str
    website_url: HttpUrl | None = None
    youtube_video_id: str | None = None
    active_job_ads: int = 0
    successful_matches: int = 0

    class Config:
        from_attribute = True

    @classmethod
    def create(cls, company: Company):
        return cls(
            id=company.id,
            name=company.name,
            address_line=company.address_line,
            city=company.city.name,
            description=company.description,
            email=company.email,
            phone_number=company.phone_number,
            active_job_ads=company.active_job_count or 0,
            successful_matches=company.successfull_matches_count or 0,
        )


class CompanyCreate(BaseModel):
    username: Username  # type: ignore
    password: Password  # type: ignore
    name: str
    address_line: str
    city: str
    description: str
    email: EmailStr
    phone_number: str

    @field_validator("password")
    def check_password(cls, password):
        if not re.match(PASSWORD_REGEX, password):
            raise ValueError(
                "Password must contain at least one lowercase letter, \
                one uppercase letter, one digit, one special character(@$!%*?&), \
                and be between 8 and 30 characters long."
            )
        return password


class CompanyUpdate(BaseModel):
    name: str | None = None
    address_line: str | None = None
    city: str | None = None
    description: str | None = None
    email: EmailStr | None = None
    phone_number: str | None = None
    website_url: HttpUrl | None = None
    youtube_video_url: HttpUrl | None = None
    youtube_video_id: str = None

    @field_validator("youtube_url", pre=True)
    def extract_video_id(cls, v, values):
        url_parts = urlparse(url=v)
        query_params = parse_qs(url_parts.query)
        video_id = query_params.get("v")
        if video_id is None:
            raise ApplicationError(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid YouTube video URL provided.",
            )
        values["youtube_video_id"] = video_id[0]
        return v


class CompanyResponse(CompanyBase):
    pass
