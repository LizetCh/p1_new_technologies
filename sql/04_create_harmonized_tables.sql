-- ============================================================
-- Restaurants (Harmonized)
-- ============================================================

CREATE TABLE IF NOT EXISTS harmonized.restaurants (
    restaurant_id      VARCHAR(50),
    restaurant_name    VARCHAR(150),
    cuisine            VARCHAR(100),
    city               VARCHAR(100),
    rating             NUMERIC(3,2),
    source_file        TEXT,
    transformed_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- Transformation procedure: Restaurants
-- ============================================================

CREATE OR REPLACE PROCEDURE automation.sp_transform_restaurants()
LANGUAGE plpgsql
AS $$
BEGIN
    TRUNCATE TABLE harmonized.restaurants;

    INSERT INTO harmonized.restaurants (
        restaurant_id,
        restaurant_name,
        cuisine,
        city,
        rating
    )
    SELECT
        restaurant_id,
        INITCAP(TRIM(restaurant_name)) AS restaurant_name,
        INITCAP(TRIM(cuisine)) AS cuisine,
        INITCAP(TRIM(city)) AS city,
        NULLIF(rating::TEXT, '')::NUMERIC(3,2) AS rating
    FROM raw.restaurants
    WHERE restaurant_id IS NOT NULL;
END;
$$;

