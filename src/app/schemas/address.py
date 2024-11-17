from uuid import UUID
from pydantic import BaseModel


class Address(BaseModel):
    address_detail: str
    city: str


class CityResponse(BaseModel):
    id: UUID
    name: str
