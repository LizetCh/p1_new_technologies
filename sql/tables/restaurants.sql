------- 1. CREATE RAW RESTAURANTS TABLE -------

CREATE TABLE IF NOT EXISTS raw.restaurants (
    restaurant_id VARCHAR(20),
    cuisine VARCHAR(100),
    city VARCHAR(100),
    rating NUMERIC(3,2),
    source_file TEXT,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-------- 2. Check Ingestion test ----------

SELECT * FROM raw.restaurants LIMIT 5;


------ 3. CREATE HARMONIZED RESTAURANTS TABLE -------

CREATE TABLE IF NOT EXISTS harmonized.restaurants (
    restaurant_id VARCHAR(20),
    cuisine VARCHAR(100),
    city VARCHAR(100),
    rating NUMERIC(3,2),
    source_file TEXT,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--------- 4. TRANSFORMATION PROCEDURE --------

--------- 4. TRANSFORMATION PROCEDURE --------

CREATE OR REPLACE PROCEDURE automation.sp_transform_restaurants()
LANGUAGE plpgsql
AS $$
BEGIN
  TRUNCATE TABLE harmonized.restaurants;

  INSERT INTO harmonized.restaurants (
    restaurant_id,
    cuisine,
    city,
    rating,
    source_file
  )
  SELECT
    TRIM(restaurant_id) AS restaurant_id,
    INITCAP(TRIM(cuisine)) AS cuisine,
    INITCAP(TRIM(city)) AS city,
    rating,
    source_file
  FROM raw.restaurants
  WHERE restaurant_id ILIKE 'R%'; -- Usamos ILIKE para atrapar tanto 'R' como 'r'
END;
$$;


----------- 5. CHECK TRANSFORMATION MANUALLY -------------

SELECT * FROM harmonized.restaurants LIMIT 5;



---------- 6. RESET AND CALL PROCEDURE TO TEST -----------

TRUNCATE TABLE harmonized.restaurants;
CALL automation.sp_transform_restaurants();
SELECT * FROM harmonized.restaurants LIMIT 5;


SELECT restaurant_id FROM raw.restaurants LIMIT 5;

------- 7. CREATE VIEW --------------

CREATE OR REPLACE VIEW analytics.vw_restaurants_summary AS
SELECT
    restaurant_id,
    cuisine,
    city,
    rating,
    -- Ejemplo de métrica agregada por tipo de cocina
    COUNT(*) OVER(PARTITION BY cuisine) AS total_in_cuisine
FROM harmonized.restaurants;

-- DROP VIEW IF EXISTS analytics.vw_restaurants_summary;

SELECT * FROM analytics.vw_restaurants_summary LIMIT 15;