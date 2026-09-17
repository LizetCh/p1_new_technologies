-- ============================================================
-- Customers
-- ============================================================

CREATE TABLE harmonized.customers (
    customer_id     VARCHAR(50),
    city            VARCHAR(100),
    signup_date     DATE,
    source_file     TEXT,
    transformed_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- Transformation procedure: Customers
-- ============================================================

CREATE OR REPLACE PROCEDURE automation.sp_transform_customers()
LANGUAGE plpgsql
AS $$
BEGIN
    TRUNCATE TABLE harmonized.customers;

    INSERT INTO harmonized.customers (
        customer_id,
        city,
        signup_date,
        source_file
    )
    SELECT
        TRIM(customer_id) AS customer_id,
        INITCAP(TRIM(city)) AS city,
        TO_DATE(signup_date, 'YYYY-MM-DD') AS signup_date,
        source_file
    FROM raw.customers
    WHERE customer_id IS NOT NULL;
END;
$$;



--Master of procedures--
CREATE OR REPLACE PROCEDURE automation.sp_transform_all()
LANGUAGE plpgsql
AS $$
BEGIN
    CALL automation.sp_transform_customers();
END;
$$;


-- ============================================================
-- Manual test
-- ============================================================

-- Before running stored procedures

SELECT COUNT (*) FROM raw.customers;

SELECT COUNT(*) FROM harmonized.customers;

CALL automation.sp_transform_customers();

