import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context
from src.app.core.config import get_settings

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from src.app.sql_app.category.category import Category
from src.app.sql_app.city.city import City
from src.app.sql_app.company.company import Company
from src.app.sql_app.company_address.company_address import CompanyAddress
from src.app.sql_app.database import Base, create_uuid_extension
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

settings = get_settings()
database_url = settings.DATABASE_URL.replace("%", "%%")

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
config.set_section_option(config.config_ini_section, "sqlalchemy.url", database_url)


# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object achere
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
create_uuid_extension()

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
