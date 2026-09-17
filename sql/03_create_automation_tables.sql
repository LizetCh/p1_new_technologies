-- ============================================================
-- Ingestion log table
-- ============================================================

-- This table tracks every CSV file processed by the ingestion pipeline.
-- It allows the pipeline to know whether a file was already loaded.
CREATE TABLE IF NOT EXISTS automation.ingestion_log (
    id SERIAL PRIMARY KEY,

    -- Logical source name.
    -- Examples: patients, doctors, appointments, treatments, billing.
    source_name TEXT NOT NULL,

    -- Relative path of the CSV file inside the project.
    -- Example: data/raw/appointments/appointments_2026_01.csv
    file_path TEXT NOT NULL,

    -- File name only.
    -- Example: appointments_2026_01.csv
    file_name TEXT NOT NULL,

    -- File size in bytes.
    -- Useful to detect whether a file changed.
    file_size BIGINT,

    -- Last modified timestamp from the operating system.
    file_modified_at TIMESTAMP,

    -- Timestamp when the pipeline processed the file.
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Processing result.
    -- Expected values: SUCCESS or FAILED.
    status TEXT NOT NULL,

    -- Number of rows loaded from the file.
    rows_loaded INTEGER DEFAULT 0,

    -- Error message if the file failed to load.
    error_message TEXT
);


-- ============================================================
-- Prevent duplicate successful loads
-- ============================================================

-- This unique index prevents the same file_path from being logged
-- more than once with status = 'SUCCESS'.
--
-- Why only SUCCESS?
-- A file can fail multiple times, but it can be marked as successfully loaded only once.
CREATE UNIQUE INDEX IF NOT EXISTS ux_ingestion_log_success_file
ON automation.ingestion_log (file_path)
WHERE status = 'SUCCESS';


-- ============================================================
-- Optional validation constraint
-- ============================================================

-- This constraint ensures only expected status values are inserted.
-- PostgreSQL does not support "IF NOT EXISTS" for CHECK constraints
-- like it does with CREATE TABLE IF NOT EXISTS or CREATE INDEX IF NOT EXISTS,
-- so this block first checks whether the constraint already exists.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'chk_ingestion_log_status'
    ) THEN
        ALTER TABLE automation.ingestion_log
        ADD CONSTRAINT chk_ingestion_log_status
        CHECK (status IN ('SUCCESS', 'FAILED'));
    END IF;
END $$;