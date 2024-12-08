from uuid import UUID

from pydantic import BaseModel

from app.sql_app.category.category import Category


class CategoryResponse(BaseModel):
    id: UUID
    title: str
    description: str
    job_ads_count: int
    job_applications_count: int

    class Config:
        from_attributes = True

    @classmethod
    def create(cls, category: Category) -> "CategoryResponse":
        return cls(
            id=category.id,
            title=category.title,
            description=category.description,
            job_ads_count=len(category.job_ads),
            job_applications_count=len(category.job_applications),
        )
