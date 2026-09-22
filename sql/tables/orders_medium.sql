
------- 1. CREATE RAW ORDERS MEDIUM TABLE -------

CREATE TABLE IF NOT EXISTS raw.orders_medium (
    order_id VARCHAR(20),
    customer_id VARCHAR(20),
    restaurant_id VARCHAR(20),
    order_time VARCHAR(20),
    delivery_time VARCHAR(50),
    status VARCHAR(20),
    source_file TEXT,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-------- 2. Check Ingestion test ----------

SELECT * FROM raw.orders_medium LIMIT 5;


------ 3. CREATE HARMONIZED ORDERS MEDIUM TABLE -------
CREATE TABLE IF NOT EXISTS harmonized.orders_medium (
    order_id VARCHAR(20),
    customer_id VARCHAR(20),
    restaurant_id VARCHAR(20),
    order_time DATE,
    delivery_time TIMESTAMP,
    status VARCHAR(20),
    source_file TEXT,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--------- 4. TRANSFORMATION PROCEDURE --------

CREATE OR REPLACE PROCEDURE automation.sp_transform_orders_medium()
LANGUAGE plpgsql
AS $$
BEGIN
  TRUNCATE TABLE harmonized.orders_medium;

  INSERT INTO harmonized.orders_medium (
    order_id,
    customer_id,
    restaurant_id,
    order_time,
    delivery_time,
    status,
    source_file
  )
  SELECT
    TRIM(order_id) AS order_id,
    TRIM(customer_id) AS customer_id,
    TRIM(restaurant_id) AS restaurant_id,
    CAST(order_time AS DATE) AS order_time,
    CAST(delivery_time AS TIMESTAMP) AS delivery_time,
    TRIM(status) AS status,
    source_file
  FROM raw.orders_medium
  WHERE order_id LIKE 'O%' 
    AND customer_id LIKE 'C%' 
    AND restaurant_id LIKE 'R%';
END;
$$;



----------- 5. CHECK TRANSFORMATION MANUALLY -------------
SELECT * FROM harmonized.orders_medium LIMIT 5;


---------- 6. RESET AND CALL PROCEDURE TO TEST -----------
TRUNCATE TABLE harmonized.orders_medium;
SELECT * FROM harmonized.orders_medium LIMIT 5;
CALL automation.sp_transform_orders_medium();
SELECT * FROM harmonized.orders_medium LIMIT 5;



------- 7. CREATE VIEW --------------

CREATE VIEW analytics.vw_delivery_performance AS
SELECT
    order_id,
    customer_id,
    restaurant_id,
    order_time,
    delivery_time,
    status,
    -- Day of the week
    TRIM(TO_CHAR(order_time, 'Day')) AS order_day_of_week,
    -- status flags
    CASE WHEN TRIM(status) = 'Late' THEN 1 ELSE 0 END AS is_late,
    CASE WHEN TRIM(status) = 'Delivered' THEN 1 ELSE 0 END AS is_delivered,
    CASE WHEN TRIM(status) = 'Cancelled' THEN 1 ELSE 0 END AS is_cancelled
FROM harmonized.orders_medium;

DROP VIEW IF EXISTS analytics.vw_delivery_performance;

SELECT * FROM analytics.vw_delivery_performance LIMIT 15;
