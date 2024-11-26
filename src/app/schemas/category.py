from pydantic import BaseModel


class CategoryResponse(BaseModel):
    id: str
    title: str
    description: str
    job_ads_count: int
    job_applications_count: int

    class Config:
        from_attributes = True

    @classmethod
    def create(cls, category) -> "CategoryResponse":
        return cls(
            id=category.id,
            title=category.title,
            description=category.description,
            job_ads_count=len(category.job_ads),
            job_applications_count=len(category.category_job_applications),
        )
