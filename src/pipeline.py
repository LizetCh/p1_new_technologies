"""
Main data pipeline.

This file runs the full pipeline:

1. Ingest new CSV files into the raw schema.
2. Run transformation stored procedures to refresh the harmonized schema.
"""

import logging

from sqlalchemy.exc import SQLAlchemyError

from ingest_files import ingest_new_files
from run_transformations import run_transformations


# ============================================================
# Logging configuration
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)



def run_pipeline() -> None:
    """
    Run the full data pipeline.

    Steps:
    1. Load new CSV files into raw tables.
    2. Run PostgreSQL stored procedures to refresh harmonized tables.
    """

    logger.info("Starting full pipeline...")

    logger.info("Step 1: Starting ingestion.")
    ingest_new_files()
    logger.info("Step 1: Ingestion completed.")

    logger.info("Step 2: Starting transformations.")
    run_transformations()
    logger.info("Step 2: Transformations completed.")

    logger.info("Full pipeline completed successfully.")


# ============================================================
# Script entry point
# ============================================================

if __name__ == "__main__":
    try:
        run_pipeline()

    except SQLAlchemyError:
        logger.exception("Database error occurred while running the pipeline.")

    except Exception:
        logger.exception("Unexpected error occurred while running the pipeline.")