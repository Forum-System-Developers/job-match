from uuid import UUID

from pydantic import BaseModel, EmailStr, PositiveInt


class CompanyBase(BaseModel):
    id: UUID
    name: str
    description: str
    email: EmailStr
    phone_number: str
    active_job_ads: PositiveInt
    successful_matches: PositiveInt

    class Config:
        from_attribute = True


class CompanyCreate(CompanyBase):
    pass


class CompanyResponse(CompanyBase):
    pass
