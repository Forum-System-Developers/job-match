import re
from urllib.parse import parse_qs, urlparse
from uuid import UUID

from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr, HttpUrl, field_validator, model_validator

from app.exceptions.custom_exceptions import ApplicationError
from app.schemas.custom_types import PASSWORD_REGEX, Password, Username


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


class CompanyCreateFinal(BaseModel):
    username: Username  # type: ignore
    password_hash: str  # type: ignore
    name: str
    address_line: str
    city_id: UUID
    description: str
    email: EmailStr
    phone_number: str


class CompanyUpdate(BaseModel):
    name: str | None = None
    address_line: str | None = None
    city: str | None = None
    description: str | None = None
    email: EmailStr | None = None
    phone_number: str | None = None
    website_url: HttpUrl | None = None
    youtube_video_url: HttpUrl | None = None
    youtube_video_id: str | None = None

    @model_validator(mode="before")
    def extract_video_id(cls, values):
        if "youtube_video_url" in values and values["youtube_video_url"]:
            url_parts = urlparse(values["youtube_video_url"])
            query_params = parse_qs(url_parts.query)
            video_id = query_params.get("v")
            if not video_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid YouTube video URL provided.",
                )
            values["youtube_video_id"] = video_id[0]
        return values


class CompanyUpdateFinal(BaseModel):
    name: str | None = None
    address_line: str | None = None
    city_id: UUID | None = None
    description: str | None = None
    email: EmailStr | None = None
    phone_number: str | None = None
    website_url: HttpUrl | None = None
    youtube_video_id: str | None = None


class CompanyResponse(CompanyBase):
    pass
