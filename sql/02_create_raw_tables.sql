-- ============================================================
-- customers_medium -> customers01
-- ============================================================

CREATE TABLE raw.customers (
    customer_id VARCHAR(50),
    city VARCHAR(100),
    signup_date VARCHAR(50),
    source_file TEXT,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SELECT * FROM raw.customers;

SELECT * FROM automation.ingestion_log;

SELECT COUNT(*) FROM raw.customers;       


