"""
File watcher.

This script watches the data/raw folder and triggers the data pipeline
when a new CSV file is detected.

This is an event-driven alternative to scheduler.py.
"""

from pathlib import Path
import logging
import time

# Monitors folders and generates file system events.
from watchdog.observers import Observer

# Base class used to define how file system events should be handled.
from watchdog.events import FileSystemEventHandler

from pipeline import run_pipeline


# ============================================================
# Logging configuration
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


# ============================================================
# Project folders
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"


# ============================================================
# File watcher handler
# ============================================================

class NewCSVFileHandler(FileSystemEventHandler):
    """
    Handles file system events inside the data/raw folder.
    """

    def __init__(self):
        self.is_pipeline_running = False

    def on_created(self, event):
        """
        Run when a new file or folder is created.
        """

        if event.is_directory:
            return

        file_path = Path(event.src_path)

        if file_path.suffix.lower() != ".csv":
            logger.info("Ignored non-CSV file: %s", file_path.name)
            return

        logger.info("New CSV file detected: %s", file_path)

        # Give Windows time to finish copying the file.
        time.sleep(2)

        self.run_pipeline_safely()

    def on_moved(self, event):
        """
        Run when a file is moved into the watched folder.

        This is useful because Windows may detect a copy-and-paste
        operation as a move event instead of a create event.
        """

        if event.is_directory:
            return

        file_path = Path(event.dest_path)

        if file_path.suffix.lower() != ".csv":
            logger.info("Ignored moved non-CSV file: %s", file_path.name)
            return

        logger.info("CSV file moved into folder: %s", file_path)

        # Give Windows time to finish moving the file.
        time.sleep(2)

        self.run_pipeline_safely()

    def run_pipeline_safely(self):
        """
        Run the pipeline safely so the watcher does not stop
        if the pipeline fails.
        """

        if self.is_pipeline_running:
            logger.warning("Pipeline is already running. Event ignored.")
            return

        self.is_pipeline_running = True

        try:
            logger.info("Starting pipeline because a new file was detected.")
            run_pipeline()
            logger.info("Pipeline completed successfully.")

        except Exception:
            logger.exception("Pipeline failed after file detection.")

        finally:
            self.is_pipeline_running = False


# ============================================================
# Main watcher function
# ============================================================

def start_file_watcher() -> None:
    """
    Start watching the data/raw folder continuously.
    """

    logger.info("Starting file watcher.")
    logger.info("Project root: %s", BASE_DIR)
    logger.info("Watching folder: %s", RAW_DATA_DIR)

    if not RAW_DATA_DIR.exists():
        raise FileNotFoundError(
            f"Raw data folder does not exist: {RAW_DATA_DIR}"
        )

    event_handler = NewCSVFileHandler()
    observer = Observer()

    observer.schedule(
        event_handler,
        path=str(RAW_DATA_DIR),
        recursive=True,
    )

    observer.start()

    logger.info("File watcher is running. Press Ctrl + C to stop.")

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Stopping file watcher.")
        observer.stop()

    observer.join()


# ============================================================
# Script entry point
# ============================================================

if __name__ == "__main__":
    try:
        start_file_watcher()

    except Exception:
        logger.exception("File watcher stopped unexpectedly.")