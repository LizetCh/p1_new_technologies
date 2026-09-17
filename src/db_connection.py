"""
Database connection helper.

This file centralizes the PostgreSQL connection logic so the rest of the
project can reuse the same database configuration.

The connection credentials are loaded from the .env file located at the
root of the project.
"""

from pathlib import Path
import os
import logging

from dotenv import load_dotenv
from sqlalchemy import create_engine, URL
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError


# ============================================================
# Logging configuration
# ============================================================

# Configure logging to show messages in the terminal only.
# No log file is created.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

# Create a logger for this file.
logger = logging.getLogger(__name__)


# ============================================================
# Load environment variables
# ============================================================

# BASE_DIR points to the root folder of the project.
# Example:
# If this file is located at:
# hospital_analytics_project/src/db_connection.py
#
# Then BASE_DIR will be:
# hospital_analytics_project
BASE_DIR = Path(__file__).resolve().parent.parent

# Path to the .env file located at the project root.
ENV_PATH = BASE_DIR / ".env"

# Load environment variables from the .env file.
load_dotenv(ENV_PATH)


# ============================================================
# Database configuration
# ============================================================

# Read database connection values from environment variables.
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")


def validate_database_variables() -> None:
    """
    Validate that all required database environment variables exist.

    Raises:
        ValueError: If any required environment variable is missing.
    """

    required_vars = {
        "DB_USER": DB_USER,
        "DB_PASSWORD": DB_PASSWORD,
        "DB_HOST": DB_HOST,
        "DB_PORT": DB_PORT,
        "DB_NAME": DB_NAME,
    }

    missing_vars = [
        key for key, value in required_vars.items()
        if not value
    ]

    if missing_vars:
        logger.error(
            "Missing required database environment variables: %s",
            ", ".join(missing_vars)
        )

        raise ValueError(
            "Missing required database environment variables: "
            + ", ".join(missing_vars)
        )

    logger.info("Database environment variables validated successfully.")


def get_database_url() -> URL:
    """
    Build and return the PostgreSQL SQLAlchemy connection URL.

    Returns:
        PostgreSQL database URL used by SQLAlchemy.
    """

    validate_database_variables()

    logger.info(
        "Building database URL for host=%s, port=%s, database=%s, user=%s",
        DB_HOST,
        DB_PORT,
        DB_NAME,
        DB_USER
    )

    return URL.create(
        drivername="postgresql+psycopg2",
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=int(DB_PORT),
        database=DB_NAME,
    )


def get_engine() -> Engine:
    """
    Create and return a SQLAlchemy engine.

    The engine is used by pandas, SQLAlchemy, and Streamlit to connect
    to PostgreSQL.

    Returns:
        SQLAlchemy Engine object.
    """

    database_url = get_database_url()

    logger.info("Creating SQLAlchemy engine.")

    return create_engine(database_url)


def test_connection() -> None:
    """
    Test the connection to PostgreSQL.

    This function is useful when students want to verify that their
    .env file and PostgreSQL database are configured correctly.
    """

    logger.info("Testing PostgreSQL connection.")

    engine = get_engine()

    with engine.connect() as conn:
        result = conn.exec_driver_sql("SELECT current_database();").scalar()

    logger.info("Connected successfully to database: %s", result)


# ============================================================
# Script entry point
# ============================================================

# This allows students to run:
# python src/db_connection.py
#
# If the connection is correct, they will see a success message.
if __name__ == "__main__":
    try:
        test_connection()

    except SQLAlchemyError:
        logger.exception("Database connection test failed.")

    except Exception:
        logger.exception(
            "Unexpected error occurred while testing the database connection."
        )