# pathlib is used to work with file and folder paths in a clean way.
# It is preferable to manually concatenating strings for paths.
from pathlib import Path

# datetime is used to register when files were loaded or processed.
from datetime import datetime

# Displays informational and error messages in the terminal.
import logging

# pandas is used to read CSV files and load them into PostgreSQL.
import pandas as pd

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

# Configure logging to show messages in the terminal only.
# No log file is created.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

# Create a logger for this file.
logger = logging.getLogger(__name__)



# ============================================================
# Database connection
# ============================================================

# Create a reusable SQLAlchemy engine.
# This engine is used by pandas and SQLAlchemy to connect to PostgreSQL.
engine = get_engine()


# ============================================================
# Project folders
# ============================================================

# BASE_DIR points to the root folder of the project.
# Example:
# If this file is located at:
# hospital_analytics_project/src/ingest_files.py
#
# Then BASE_DIR will be:
# hospital_analytics_project
BASE_DIR = Path(__file__).resolve().parent.parent

# RAW_DATA_DIR points to the folder where raw CSV files are stored.
# Expected structure:
# data/raw/orders_medium/
# TODO: Agregar la carpeta de raw para los otros CSVs
RAW_DATA_DIR = BASE_DIR / "data" / "raw"

# ============================================================
# Source configuration
# ============================================================

# SOURCES maps each type of CSV file to:
# 1. the folder where the files are located
# 2. the PostgreSQL schema
# 3. the PostgreSQL table where the data should be loaded
#
# Example:
# CSV files in data/raw/appointments/
# will be loaded into raw.appointments
SOURCES = {
    "orders_medium": {
        "folder": RAW_DATA_DIR / "orders_medium",
        "schema": "raw",
        "table": "orders_medium",
    },
    # TODO: Agregar match para otras carpetas de raw y sus tablas correspondientes
}


# ============================================================
# Helper functions
# ============================================================

def get_relative_path(file_path: Path) -> str:
    r"""
    Return the file path relative to BASE_DIR, which is the project root.

    Example:
    BASE_DIR = C:\Users\crist\Documents\hospital_analytics_project

    The function converts:
    C:\Users\crist\Documents\hospital_analytics_project\data\raw\patients\patients.csv

    into:
    data\raw\patients\patients.csv

    This avoids storing a full path that only works on one computer.
    """
    return str(file_path.relative_to(BASE_DIR))

def get_csv_files(folder_path: Path) -> list[Path]:
    """
    Return all CSV files from a folder.

    Parameters:
        folder_path: Path to the folder that contains CSV files.

    Returns:
        A sorted list of CSV file paths.
    """

    # If the folder does not exist, log a warning and return an empty list.
    # This prevents the script from failing if one source folder is missing.
    if not folder_path.exists():
        logger.warning("Folder does not exist: %s", folder_path)
        return []

    # Find all files ending in .csv inside the folder.
    # sorted() makes the loading order predictable.
    return sorted(folder_path.glob("*.csv"))

def file_was_processed(file_path: Path) -> bool:
    """
    Check if a file was already processed successfully.

    This function checks the automation.ingestion_log table.
    If the file path exists with status = 'SUCCESS', the file is skipped.

    Parameters:
        file_path: Path of the CSV file.

    Returns:
        True if the file was already processed successfully.
        False if the file has not been processed yet.
    """

    relative_file_path = get_relative_path(file_path)

    # SQL query to count successful records for this specific file.
    # :file_path is a safe parameter placeholder.
    query = text("""
        SELECT COUNT(*) AS total
        FROM automation.ingestion_log
        WHERE file_path = :file_path
          AND status = 'SUCCESS'
    """)

    # Open a database connection.
    with engine.connect() as conn:
        # Execute the query and pass the file path as a parameter.
        result = conn.execute(
            query,
            {"file_path": relative_file_path}
        ).scalar()

    # If the count is greater than 0, the file was already processed.
    return result > 0


def log_ingestion(
    source_name: str,
    file_path: Path,
    status: str,
    rows_loaded: int = 0,
    error_message: str | None = None
) -> None:
    """
    Insert a record into automation.ingestion_log.

    This function records whether a file was processed successfully or failed.

    Parameters:
        source_name: Name of the source, such as patients, appointments, billing.
        file_path: Path of the CSV file.
        status: SUCCESS or FAILED.
        rows_loaded: Number of rows inserted into the raw table.
        error_message: Error message if the process failed.
    """

    relative_file_path = get_relative_path(file_path)

    # Get the file size in bytes.
    # If the file does not exist, use None.
    file_size = file_path.stat().st_size if file_path.exists() else None

    # Get the last modified timestamp of the file.
    # This is useful for auditing and troubleshooting.
    file_modified_at = (
        datetime.fromtimestamp(file_path.stat().st_mtime)
        if file_path.exists()
        else None
    )

    # Insert one row into the ingestion log table.
    query = text("""
        INSERT INTO automation.ingestion_log (
            source_name,
            file_path,
            file_name,
            file_size,
            file_modified_at,
            processed_at,
            status,
            rows_loaded,
            error_message
        )
        VALUES (
            :source_name,
            :file_path,
            :file_name,
            :file_size,
            :file_modified_at,
            :processed_at,
            :status,
            :rows_loaded,
            :error_message
        )
    """)

    # engine.begin() opens a transaction.
    # If the insert succeeds, it commits automatically.
    # If it fails, it rolls back automatically.
    with engine.begin() as conn:
        conn.execute(
            query,
            {
                "source_name": source_name,
                "file_path": relative_file_path,
                "file_name": file_path.name,
                "file_size": file_size,
                "file_modified_at": file_modified_at,
                "processed_at": datetime.now(),
                "status": status,
                "rows_loaded": rows_loaded,
                "error_message": error_message,
            }
        )

def load_csv_to_raw_table(
    file_path: Path,
    schema_name: str,
    table_name: str
) -> int:
    """
    Load a CSV file into the corresponding raw table.

    This function:
    1. Reads the CSV file into a pandas DataFrame.
    2. Adds metadata columns: source_file and loaded_at.
    3. Appends the data into the PostgreSQL raw table.

    Parameters:
        file_path: Path of the CSV file.
        schema_name: PostgreSQL schema name, usually raw.
        table_name: PostgreSQL table name.

    Returns:
        Number of rows loaded.
    """

    # Read the CSV file into a pandas DataFrame.
    df = pd.read_csv(file_path)

    # Prevent loading empty files.
    if df.empty:
        logger.warning("File is empty: %s", file_path.name)
        return 0

    # Add the source file name to every row.
    # This helps track where each record came from.
    df["source_file"] = file_path.name

    # Add the timestamp when the file was loaded.
    df["loaded_at"] = datetime.now()

    # Append the DataFrame into the target PostgreSQL table.
    # if_exists="append" means the table must already exist,
    # and new rows will be inserted without deleting existing data.
    df.to_sql(
        name=table_name,
        con=engine,
        schema=schema_name,
        if_exists="append",
        index=False
    )

    # Return the number of rows inserted.
    return len(df)


def process_file(
    source_name: str,
    file_path: Path,
    schema_name: str,
    table_name: str
) -> None:
    """
    Process one CSV file.

    Steps:
    1. Check if the file was already processed.
    2. If yes, skip it.
    3. If no, load it into the raw table.
    4. Log SUCCESS or FAILED in automation.ingestion_log.

    Parameters:
        source_name: Name of the source, such as patients or appointments.
        file_path: Path of the CSV file.
        schema_name: PostgreSQL schema name.
        table_name: PostgreSQL table name.
    """

    # Skip the file if it was already processed successfully.
    if file_was_processed(file_path):
        logger.info("Skipped already processed file: %s", file_path.name)
        return

    logger.info("Processing new file: %s", file_path.name)

    try:
        # Load the CSV data into the raw PostgreSQL table.
        rows_loaded = load_csv_to_raw_table(
            file_path=file_path,
            schema_name=schema_name,
            table_name=table_name
        )

        # If the load succeeds, record a SUCCESS entry in the ingestion log.
        log_ingestion(
            source_name=source_name,
            file_path=file_path,
            status="SUCCESS",
            rows_loaded=rows_loaded,
            error_message=None
        )

        logger.info("Loaded %s rows from %s", rows_loaded, file_path.name)

    except Exception as e:
        # If anything fails, capture the error message.
        error_message = str(e)

        # Record a FAILED entry in the ingestion log.
        # This is useful for auditing and debugging.
        log_ingestion(
            source_name=source_name,
            file_path=file_path,
            status="FAILED",
            rows_loaded=0,
            error_message=error_message
        )

        # logger.exception logs the error message plus the full traceback.
        logger.exception("Failed to load %s", file_path.name)


def ingest_new_files() -> None:
    """
    Main ingestion function.

    This function scans all configured raw folders and loads only new CSV files.
    """

    logger.info("Starting ingestion process...")

    # Loop through every configured source:
    # patients, doctors, appointments, treatments, billing.
    for source_name, config in SOURCES.items():

        # Get the folder path and target database table for this source.
        folder_path = config["folder"]
        schema_name = config["schema"]
        table_name = config["table"]

        logger.info("Checking source: %s", source_name)
        logger.info("Folder: %s", folder_path)

        # Get all CSV files from the source folder.
        csv_files = get_csv_files(folder_path)

        # If there are no CSV files, continue with the next source.
        if not csv_files:
            logger.info("No CSV files found for source: %s", source_name)
            continue

        # Process each CSV file one by one.
        for file_path in csv_files:
            process_file(
                source_name=source_name,
                file_path=file_path,
                schema_name=schema_name,
                table_name=table_name
            )

    logger.info("Ingestion process completed.")


# ============================================================
# Script entry point
# ============================================================

# This block runs only when the file is executed directly:
# python src/ingest_files.py
#
# It does not run when the file is imported by another file,
# such as pipeline.py.
if __name__ == "__main__":
    try:
        # Start the ingestion process.
        ingest_new_files()

    except SQLAlchemyError:
        # Catch database-specific errors.
        logger.exception("Database error occurred.")

    except Exception:
        # Catch any unexpected error.
        logger.exception("Unexpected error occurred.")