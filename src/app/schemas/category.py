from uuid import UUID

from pydantic import BaseModel


class CategoryResponse(BaseModel):
    id: UUID
    title: str
    description: str
    job_ads_count: int
    job_applications_count: int

    class Config:
        from_attributes = True
