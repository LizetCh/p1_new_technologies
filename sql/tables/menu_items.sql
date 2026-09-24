--- 1. Create raw table ---

CREATE TABLE IF NOT EXISTS raw.menu_items (
    item_id VARCHAR(10),
    restaurant_id VARCHAR(10),
    price VARCHAR (10),
    source_file TEXT,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

--- 2. Test ---

SELECT * FROM raw.menu_items LIMIT 20;

--- 3. Create harmonized table ---

CREATE TABLE IF NOT EXISTS harmonized.menu_items (
    item_id VARCHAR(10),
    restaurant_id VARCHAR(10),
    price NUMERIC(10, 2),
    source_file TEXT,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

--- 4. Create procedure ---

CREATE OR REPLACE PROCEDURE automation.sp_transform_menu_items()
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO harmonized.menu_items (
        item_id,
        restaurant_id,
        price,
        source_file
    ) SELECT
        TRIM(item_id) as item_id,
        TRIM(restaurant_id) as restaurant_id,
        REGEXP_REPLACE(
            TRIM(price),
            '[^0-9.]',
            '',
            'g'
        )::NUMERIC(10, 2)
        source_file
    FROM raw.menu_items
    WHERE
        item_id LIKE 'M%'
        AND restaurant_id LIKE 'R%';
END;
$$;

--- 5. Check procedure result manually ---

SELECT * FROM harmonized.menu_items LIMIT 5;

--- 6. Reset and call procedure ---

TRUNCATE TABLE harmonized.menu_items;
SELECT * FROM harmonized.menu_items LIMIT 5;
CALL automation.sp_transform_menu_items();
SELECT * FROM harmonized.menu_items LIMIT 5;

--- 7. Create view ---

CREATE OR REPLACE VIEW analytics.vw_menu_items AS
SELECT 
    restaurant_id,
    COUNT(item_id) AS total_items,
    ROUND(AVG(price), 2) AS average_price,
    MIN(price) AS minimum_price,
    MAX(price) AS maximum_price,
    ROUND(STDDEV(price), 2) AS std_deviation_price
FROM 
    harmonized.menu_items
GROUP BY 
    restaurant_id;