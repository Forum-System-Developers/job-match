import random
from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

from sqlalchemy.orm import Session

from app.sql_app import (
    Category,
    CategoryJobApplication,
    City,
    Company,
    JobAd,
    JobAdSkill,
    JobApplication,
    JobApplicationSkill,
    Match,
    PendingSkill,
    Professional,
    Skill,
)
from app.sql_app.job_ad.job_ad_status import JobAdStatus
from app.sql_app.job_application.job_application_status import JobStatus
from app.sql_app.job_requirement.skill_level import SkillLevel
from app.sql_app.match.match_status import MatchStatus
from app.sql_app.professional.professional_status import ProfessionalStatus
from app.utils.password_utils import hash_password


def random_date_within_last_month() -> datetime:
    now = datetime.now()
    one_month_ago = now - timedelta(days=30)
    return one_month_ago + (now - one_month_ago) * random.random()


def ensure_valid_created_at(target_date: datetime) -> datetime:
    while (valid_datetime := random_date_within_last_month()) <= target_date:
        pass
    return valid_datetime


cities = [
    {
        "id": uuid4(),
        "name": "City1",
    },
    {
        "id": uuid4(),
        "name": "City2",
    },
    {
        "id": uuid4(),
        "name": "City3",
    },
    {
        "id": uuid4(),
        "name": "City4",
    },
]

categories = [
    {
        "id": uuid4(),
        "title": "IT",
        "description": "Information Technology",
    },
    {
        "id": uuid4(),
        "title": "Marketing",
        "description": "Marketing",
    },
    {
        "id": uuid4(),
        "title": "Logistics",
        "description": "Logistics",
    },
]

companies: list[dict[str, Any]] = [
    {
        "id": uuid4(),
        "city_id": cities[0]["id"],
        "username": "company1",
        "password": hash_password("Company1pwd!"),
        "name": "Company 1",
        "description": "Company 1 description",
        "address_line": "Company 1 address",
        "email": "company1@example.com",
        "phone_number": "1234567890",
        "created_at": random_date_within_last_month(),
    },
    {
        "id": uuid4(),
        "city_id": cities[1]["id"],
        "username": "company2",
        "password": hash_password("Company2pwd!"),
        "name": "Company 2",
        "description": "Company 2 description",
        "address_line": "Company 2 address",
        "email": "company2@exmaple.com",
        "phone_number": "0987654321",
        "created_at": random_date_within_last_month(),
    },
    {
        "id": uuid4(),
        "city_id": cities[2]["id"],
        "username": "company3",
        "password": hash_password("Company3pwd!"),
        "name": "Company 3",
        "description": "Company 3 description",
        "address_line": "Company 3 address",
        "email": "company3@example.com",
        "phone_number": "1357924680",
        "created_at": random_date_within_last_month(),
    },
]

professionals: list[dict[str, Any]] = [
    {
        "id": uuid4(),
        "city_id": cities[0]["id"],
        "first_name": "Professional 1",
        "last_name": "Professional 1",
        "username": "professional1",
        "password": hash_password("Professional1pwd!"),
        "description": "Professional 1 description",
        "email": "professional1@example.com",
        "status": ProfessionalStatus.ACTIVE,
        "active_application_count": 0,
        "has_private_matches": False,
        "created_at": random_date_within_last_month(),
    },
    {
        "id": uuid4(),
        "city_id": cities[1]["id"],
        "first_name": "Professional 2",
        "last_name": "Professional 2",
        "username": "professional2",
        "password": hash_password("Professional2pwd!"),
        "description": "Professional 2 description",
        "email": "professional2@example.com",
        "status": ProfessionalStatus.ACTIVE,
        "active_application_count": 0,
        "has_private_matches": False,
        "created_at": random_date_within_last_month(),
    },
    {
        "id": uuid4(),
        "city_id": cities[2]["id"],
        "first_name": "Professional 3",
        "last_name": "Professional 3",
        "username": "professional3",
        "password": hash_password("Professional3pwd!"),
        "description": "Professional 3 description",
        "email": "professional3@example.com",
        "status": ProfessionalStatus.ACTIVE,
        "active_application_count": 0,
        "has_private_matches": False,
        "created_at": random_date_within_last_month(),
    },
]

skills = [
    {
        "id": uuid4(),
        "name": "Skill 1",
        "category_id": categories[0]["id"],
    },
    {
        "id": uuid4(),
        "name": "Skill 2",
        "category_id": categories[1]["id"],
    },
    {
        "id": uuid4(),
        "name": "Skill 3",
        "category_id": categories[2]["id"],
    },
]

pending_skills = [
    {
        "id": uuid4(),
        "category_id": categories[0]["id"],
        "submitted_by": companies[0]["id"],
        "name": "Pending Skill 1",
        "created_at": ensure_valid_created_at(companies[0]["created_at"]),
    },
]

job_ads = [
    {
        "id": uuid4(),
        "company_id": companies[0]["id"],
        "category_id": categories[0]["id"],
        "location_id": cities[0]["id"],
        "title": "Job Ad 1",
        "description": "Job Ad 1 description",
        "min_salary": 1000.0,
        "max_salary": 2000.0,
        "skill_level": SkillLevel.INTERMEDIATE,
        "status": JobAdStatus.ACTIVE,
        "created_at": random_date_within_last_month(),
    },
    {
        "id": uuid4(),
        "company_id": companies[1]["id"],
        "category_id": categories[1]["id"],
        "location_id": cities[1]["id"],
        "title": "Job Ad 2",
        "description": "Job Ad 2 description",
        "min_salary": 2000.0,
        "max_salary": 3000.0,
        "skill_level": SkillLevel.ADVANCED,
        "status": JobAdStatus.ACTIVE,
        "created_at": random_date_within_last_month(),
    },
    {
        "id": uuid4(),
        "company_id": companies[2]["id"],
        "category_id": categories[2]["id"],
        "location_id": cities[2]["id"],
        "title": "Job Ad 3",
        "description": "Job Ad 3 description",
        "min_salary": 3000.0,
        "max_salary": 4000.0,
        "skill_level": SkillLevel.EXPERT,
        "status": JobAdStatus.ACTIVE,
        "created_at": random_date_within_last_month(),
    },
]

job_ad_skills = [
    {
        "job_ad_id": job_ads[0]["id"],
        "skill_id": skills[0]["id"],
    },
    {
        "job_ad_id": job_ads[1]["id"],
        "skill_id": skills[1]["id"],
    },
    {
        "job_ad_id": job_ads[2]["id"],
        "skill_id": skills[2]["id"],
    },
]

job_applications = [
    {
        "id": uuid4(),
        "city_id": cities[0]["id"],
        "professional_id": professionals[0]["id"],
        "description": "Job Application 1",
        "min_salary": 1000.0,
        "max_salary": 2000.0,
        "status": JobStatus.ACTIVE,
        "is_main": False,
        "created_at": ensure_valid_created_at(professionals[0]["created_at"]),
    },
    {
        "id": uuid4(),
        "city_id": cities[1]["id"],
        "professional_id": professionals[1]["id"],
        "description": "Job Application 2",
        "min_salary": 2000.0,
        "max_salary": 3000.0,
        "status": JobStatus.ACTIVE,
        "is_main": False,
        "created_at": ensure_valid_created_at(professionals[1]["created_at"]),
    },
    {
        "id": uuid4(),
        "city_id": cities[2]["id"],
        "professional_id": professionals[2]["id"],
        "description": "Job Application 3",
        "min_salary": 3000.0,
        "max_salary": 4000.0,
        "status": JobStatus.ACTIVE,
        "is_main": False,
        "created_at": ensure_valid_created_at(professionals[2]["created_at"]),
    },
]

job_application_skills = [
    {
        "job_application_id": job_applications[0]["id"],
        "skill_id": skills[0]["id"],
    },
    {
        "job_application_id": job_applications[1]["id"],
        "skill_id": skills[1]["id"],
    },
    {
        "job_application_id": job_applications[2]["id"],
        "skill_id": skills[2]["id"],
    },
]

category_job_applications = [
    {
        "category_id": categories[0]["id"],
        "job_application_id": job_applications[0]["id"],
    },
    {
        "category_id": categories[1]["id"],
        "job_application_id": job_applications[1]["id"],
    },
    {
        "category_id": categories[2]["id"],
        "job_application_id": job_applications[2]["id"],
    },
]

matches = [
    {
        "job_ad_id": job_ads[0]["id"],
        "job_application_id": job_applications[0]["id"],
        "status": MatchStatus.REQUESTED_BY_JOB_AD,
        "created_at": ensure_valid_created_at(
            max(job_applications[0]["created_at"], job_ads[0]["created_at"])
        ),
    },
    {
        "job_ad_id": job_ads[1]["id"],
        "job_application_id": job_applications[1]["id"],
        "status": MatchStatus.REQUESTED_BY_JOB_APP,
        "created_at": ensure_valid_created_at(
            max(job_applications[1]["created_at"], job_ads[1]["created_at"])
        ),
    },
    {
        "job_ad_id": job_ads[2]["id"],
        "job_application_id": job_applications[2]["id"],
        "status": MatchStatus.ACCEPTED,
        "created_at": ensure_valid_created_at(
            max(job_applications[2]["created_at"], job_ads[2]["created_at"])
        ),
    },
]


def insert_cities(db: Session) -> None:
    for city in cities:
        city_model = City(**city)
        db.add(city_model)
    db.commit()


def insert_categories(db: Session) -> None:
    for category in categories:
        category_model = Category(**category)
        db.add(category_model)
    db.commit()


def insert_companies(db: Session) -> None:
    for company in companies:
        company_model = Company(**company)
        db.add(company_model)
    db.commit()


def insert_professionals(db: Session) -> None:
    for professional in professionals:
        professional_model = Professional(**professional)
        db.add(professional_model)
    db.commit()


def insert_job_ads(db: Session) -> None:
    for job_ad in job_ads:
        job_ad_model = JobAd(**job_ad)
        db.add(job_ad_model)
    db.commit()


def insert_job_ad_skills(db: Session) -> None:
    for job_ad_skill in job_ad_skills:
        job_ad_skill_model = JobAdSkill(**job_ad_skill)
        db.add(job_ad_skill_model)
    db.commit()


def insert_job_applications(db: Session) -> None:
    for job_application in job_applications:
        job_application_model = JobApplication(**job_application)
        db.add(job_application_model)
    db.commit()


def insert_skills(db: Session) -> None:
    for skill in skills:
        skill_model = Skill(**skill)
        db.add(skill_model)
    db.commit()


def insert_pending_skills(db: Session) -> None:
    for pending_skill in pending_skills:
        pending_skill_model = PendingSkill(**pending_skill)
        db.add(pending_skill_model)
    db.commit()


def insert_job_application_skills(db: Session) -> None:
    for job_application_skill in job_application_skills:
        job_application_skill_model = JobApplicationSkill(**job_application_skill)
        db.add(job_application_skill_model)
    db.commit()


def insert_category_job_applications(db: Session) -> None:
    for category_job_application in category_job_applications:
        category_job_application_model = CategoryJobApplication(
            **category_job_application
        )
        db.add(category_job_application_model)
    db.commit()


def insert_matches(db: Session) -> None:
    for match in matches:
        match_model = Match(**match)
        db.add(match_model)
    db.commit()


def insert_data(db: Session) -> None:
    insert_cities(db)
    insert_categories(db)
    insert_companies(db)
    insert_professionals(db)
    insert_skills(db)
    insert_pending_skills(db)
    insert_job_ads(db)
    insert_job_ad_skills(db)
    insert_job_applications(db)
    insert_job_application_skills(db)
    insert_category_job_applications(db)
    insert_matches(db)
