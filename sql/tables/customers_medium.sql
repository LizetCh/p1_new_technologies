------- 1. CREATE RAW CUSTOMERS MEDIUM TABLE -------

CREATE TABLE IF NOT EXISTS raw.customers_medium (
    customer_id VARCHAR(20),
    city VARCHAR(50),
    signup_date VARCHAR(20),
    source_file TEXT,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-------- 2. Check Ingestion test ----------

SELECT * FROM raw.customers_medium LIMIT 5;


------ 3. CREATE HARMONIZED CUSTOMERS MEDIUM TABLE -------
CREATE TABLE IF NOT EXISTS harmonized.customers_medium (
    customer_id VARCHAR(20),
    city VARCHAR(50),
    signup_date DATE,
    source_file TEXT,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--------- 4. TRANSFORMATION PROCEDURE --------
--
-- Business rules:
-- 1. Validate customer_id starts with 'C'.
-- 2. Standardize city using title case.
-- 3. Cast signup_date to DATE.

CREATE OR REPLACE PROCEDURE automation.sp_transform_customers_medium()
LANGUAGE plpgsql
AS $$
BEGIN
  TRUNCATE TABLE harmonized.customers_medium;

  INSERT INTO harmonized.customers_medium (
    customer_id,
    city,
    signup_date,
    source_file
  )
  SELECT
    TRIM(customer_id) AS customer_id,
    INITCAP(TRIM(city)) AS city,
    CAST(signup_date AS DATE) AS signup_date,
    source_file
  FROM raw.customers_medium
  WHERE customer_id LIKE 'C%';
END;
$$;


----------- 5. CHECK TRANSFORMATION MANUALLY -------------
SELECT * FROM harmonized.customers_medium LIMIT 5;


---------- 6. RESET AND CALL PROCEDURE TO TEST -----------
TRUNCATE TABLE raw.customers_medium;
TRUNCATE TABLE harmonized.customers_medium;
SELECT * FROM harmonized.customers_medium LIMIT 5;
CALL automation.sp_transform_customers_medium();
SELECT * FROM harmonized.customers_medium LIMIT 5;


------- 7. CREATE VIEWS --------------

CREATE OR REPLACE VIEW analytics.vw_customers_by_city AS
SELECT
    city,
    COUNT(*) AS total_customers
FROM harmonized.customers_medium
GROUP BY city
ORDER BY total_customers DESC;

SELECT * FROM analytics.vw_customers_by_city;


DROP VIEW IF EXISTS analytics.vw_customer_signups_by_month;

CREATE OR REPLACE VIEW analytics.vw_customer_signups_by_month AS
SELECT
    EXTRACT(YEAR FROM signup_date)::INT AS signup_year,
    EXTRACT(MONTH FROM signup_date)::INT AS signup_month_number,
    TRIM(TO_CHAR(signup_date, 'Month')) AS signup_month_name,
    COUNT(*) AS total_signups
FROM harmonized.customers_medium
GROUP BY
    EXTRACT(YEAR FROM signup_date),
    EXTRACT(MONTH FROM signup_date),
    TRIM(TO_CHAR(signup_date, 'Month'))
ORDER BY signup_year, signup_month_number;

SELECT * FROM analytics.vw_customer_signups_by_month;


--Test--
SELECT COUNT(*) FROM raw.customers_medium;            
SELECT COUNT(*) FROM harmonized.customers_medium;      
SELECT customer_id, COUNT(*) FROM harmonized.customers_medium
  GROUP BY customer_id HAVING COUNT(*) > 1;            
SELECT * FROM analytics.vw_customers_by_city;          
SELECT * FROM analytics.vw_customer_signups_by_month;  