from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.schemas.custom_types import Password, Username
from app.sql_app.company.company import Company


class CompanyBase(BaseModel):
    id: UUID
    name: str
    address_line: str
    city_id: UUID
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
            city_id=company.city_id,
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
    city_id: UUID
    description: str
    email: EmailStr
    phone_number: str


class CompanyUpdate(BaseModel):
    name: str | None
    address_line: str | None
    city: str | None
    description: str | None
    email: EmailStr | None
    phone_number: str | None


class CompanyResponse(CompanyBase):
    pass
