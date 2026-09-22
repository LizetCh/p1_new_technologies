--- 1. Create raw table ---

CREATE TABLE IF NOT EXISTS raw.menu_items (
    item_id VARCHAR(10),
    restaurant_id VARCHAR(10),
    price VARCHAR (10),
    source_file TEXT,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

--- 2. Test ---

SELECT * FROM raw.menu_items LIMIT 5;

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

    TRUNCATE TABLE harmonized.menu_items;

    INSERT INTO harmonized.menu_items (
        item_id,
        restaurant_id,
        price,
        source_file
    ) SELECT
        TRIM(item_id) as item_id,
        TRIM(restaurant_id) as restaurant_id,
        price,
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