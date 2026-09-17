CREATE SCHEMA IF NOT EXISTS harmonized;

DROP TABLE IF EXISTS harmonized.restaurants;

-- Crear la tabla armonizada de restaurantes
CREATE TABLE harmonized.restaurants (
    restaurant_id VARCHAR(50) PRIMARY KEY,
    cuisine VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    rating NUMERIC(3, 2)
);

INSERT INTO harmonized.restaurants (restaurant_id, cuisine, city, rating)
SELECT 
    restaurant_id,
    cuisine,
    city,
    rating
FROM raw.restaurants
WHERE restaurant_id IS NOT NULL;


-- ============================================================
-- Manual test
-- ============================================================

SELECT COUNT(*) FROM raw.restaurants;
Select * from harmonized.restaurants;