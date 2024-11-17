from uuid import UUID

from pydantic import BaseModel, EmailStr, PositiveInt

from app.schemas.address import Address


class CompanyBase(BaseModel):
    id: UUID
    name: str
    address: Address
    description: str
    email: EmailStr
    phone_number: str
    active_job_ads: PositiveInt
    successful_matches: PositiveInt

    class Config:
        from_attribute = True


class CompanyCreate(BaseModel):
    username: str
    password: str
    name: str
    address: Address
    description: str
    email: EmailStr
    phone_number: str


class CompanyUpdate(BaseModel):
    name: str | None
    address: Address | None
    description: str | None
    email: EmailStr | None
    phone_number: str | None


class CompanyResponse(CompanyBase):
    pass
