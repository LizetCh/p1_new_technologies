"""
Run PostgreSQL transformation stored procedures.

This file calls the stored procedures that transform data from the raw schema
into the harmonized schema.
"""

# Displays informational and error messages in the terminal.
import logging

# text is used to safely execute SQL queries with parameters.
from sqlalchemy import text

# SQLAlchemyError is used to catch database-related errors.
from sqlalchemy.exc import SQLAlchemyError

# get_engine centralizes the database connection logic.
# The credentials are handled in src/db_connection.py using the .env file.
from db_connection import get_engine


# ============================================================
# Logging configuration
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


# ============================================================
# Database connection
# ============================================================

engine = get_engine()


# ============================================================
# Transformation logic
# ============================================================

def run_transformations() -> None:
    """
    Run all transformation stored procedures.

    This function calls the master stored procedure:

        automation.sp_transform_all()

    The master procedure is responsible for refreshing all harmonized tables.
    """

    logger.info("Starting transformation process...")

    query = text("CALL automation.sp_transform_all();")

    with engine.begin() as conn:
        conn.execute(query)

    logger.info("Transformation process completed successfully.")


# ============================================================
# Script entry point
# ============================================================

if __name__ == "__main__":
    try:
        run_transformations()

    except SQLAlchemyError:
        logger.exception("Database error occurred while running transformations.")

    except Exception:
        logger.exception("Unexpected error occurred while running transformations.")