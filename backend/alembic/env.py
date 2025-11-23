import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# ============================================================
# 1. SETUP PATHS & IMPORTS
# ============================================================

# Add the project root to sys.path so we can import from 'src'
# This assumes env.py is in /alembic/ and your root is one level up.
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import your Base from your specific project structure
from src.adapters.base.sql_repository_base import Base

# ============================================================
# 2. INITIALIZE ALEMBIC CONFIG
# ============================================================

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the metadata so Alembic can generate autigrations
target_metadata = Base.metadata

# ============================================================
# 3. DYNAMIC DATABASE URL CONFIGURATION
# ============================================================

# Get the URL from Env Var, or fallback to your local SQLite path
db_url = os.getenv("DATABASE_URL", "sqlite:///./src/data/cities.db")

# Force Alembic to use this URL instead of the one in alembic.ini
config.set_main_option("sqlalchemy.url", db_url)


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
    
    # SAFEGUARD: Check if url exists before running startswith
    # This prevents 'NoneType has no attribute startswith'
    is_sqlite = url is not None and url.startswith("sqlite")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Enable batch mode ONLY for SQLite
        render_as_batch=is_sqlite
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    
    # Create the engine using the config object we modified earlier
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # For online mode, we can check the dialect directly from the connection
        # This is safer than checking the URL string
        is_sqlite = connection.dialect.name == "sqlite"

        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            # Enable batch mode ONLY for SQLite
            render_as_batch=is_sqlite
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()