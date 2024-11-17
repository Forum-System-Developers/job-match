from pydantic import BaseModel


class Address(BaseModel):
    address_detail: str
    city: str
