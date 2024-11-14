from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.app.core.config import get_settings

engine = create_engine(get_settings().DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


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
