from uuid import UUID

from pydantic import BaseModel, EmailStr, PositiveInt

from app.schemas.custom_types import Password, Username


class CompanyBase(BaseModel):
    id: UUID
    name: str
    address_line: str
    city: str
    description: str
    email: EmailStr
    phone_number: str
    active_job_ads: PositiveInt
    successful_matches: PositiveInt

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


class CompanyUpdate(BaseModel):
    name: str | None
    address_line: str | None
    city: str | None
    description: str | None
    email: EmailStr | None
    phone_number: str | None


class CompanyResponse(CompanyBase):
    pass
