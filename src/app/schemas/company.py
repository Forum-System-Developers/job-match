import re
from uuid import UUID

from pydantic import BaseModel, EmailStr, field_validator

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
                'Password must contain at least one lowercase letter, \
                one uppercase letter, one digit, one special character(@$!%*?&), \
                and be between 8 and 30 characters long.')
        return password


class CompanyUpdate(BaseModel):
    name: str | None
    address_line: str | None
    city: str | None
    description: str | None
    email: EmailStr | None
    phone_number: str | None


class CompanyResponse(CompanyBase):
    pass
