from sqlalchemy import create_engine, text
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.app.core.config import get_settings
from src.app.core.config import get_settings

engine = create_engine(get_settings().DATABASE_URL)
engine = create_engine(get_settings().DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

from src.app.sql_app.category.category import Category
from src.app.sql_app.city.city import City
from src.app.sql_app.company.company import Company
from src.app.sql_app.company_address.company_address import CompanyAddress
from src.app.sql_app.job_ad.job_ad import JobAd
from src.app.sql_app.job_ad_requirement.job_ads_requirement import JobAdsRequirement
from src.app.sql_app.job_application.job_application import JobApplication
from src.app.sql_app.job_application_skill.job_application_skill import (
    JobApplicationSkill,
)
from src.app.sql_app.match.match import Match
from src.app.sql_app.professional.professional import Professional
from src.app.sql_app.search_history.search_history import SearchHistory
from src.app.sql_app.skill.skill import Skill
from src.app.sql_app.user.user import User


# Dependency
def get_db():
    """
    Provides a database session for use in a context manager.

    Yields:
        db: A database session object.

    Ensures that the database session is properly closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_uuid_extension():
    """
    Creates the "uuid-ossp" extension in the connected PostgreSQL database if it does not already exist.

    This function establishes a connection to the database using the provided engine,
    begins a transaction, and executes the SQL command to create the "uuid-ossp" extension.
    The "uuid-ossp" extension provides functions to generate universally unique identifiers (UUIDs).
    """
    with engine.connect() as connection:
        with connection.begin():
            connection.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))


def create_tables():
    """
    Create all tables in the database.

    This function uses SQLAlchemy's metadata to create all tables that are defined
    in the Base class. It binds the metadata to the specified engine and creates
    the tables if they do not already exist.
    """
    Base.metadata.create_all(bind=engine)


def initialize_database():
    """
    Initialize the database by creating the tables and the "uuid-ossp" extension.

    This function calls the create_tables() and create_uuid_extension() functions
    to create the necessary tables and enable the "uuid-ossp" extension in the database.
    """
    create_uuid_extension()
    create_tables()
