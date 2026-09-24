--------- Tablas para order_items ---------

-- Zona Raw (Ingesta)
CREATE TABLE IF NOT EXISTS raw.order_items (
    order_id VARCHAR(50),
    item_id VARCHAR(50),
    quantity VARCHAR(50),
    price VARCHAR(50),
    source_file TEXT,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Zona Harmonized (Transformación)
CREATE TABLE IF NOT EXISTS harmonized.order_items (
    order_id VARCHAR(50),
    item_id VARCHAR(50),
    quantity INT,
    price NUMERIC(10,2),
    source_file TEXT,
    transformed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--------- Procedimiento de Transformación ---------
CREATE OR REPLACE PROCEDURE automation.sp_transform_order_items()
LANGUAGE plpgsql
AS $$
BEGIN
    TRUNCATE TABLE harmonized.order_items;

    INSERT INTO harmonized.order_items (order_id, item_id, quantity, price, source_file)
    SELECT order_id, item_id, CAST(quantity AS INT), CAST(price AS NUMERIC(10,2)), source_file
    FROM raw.order_items;
END;
$$;

--------- Vista para el Dashboard (Analytics) ---------
CREATE OR REPLACE VIEW analytics.vw_order_items_performance AS
SELECT 
    item_id, 
    SUM(quantity) AS total_quantity, 
    SUM(quantity * price) AS total_revenue
FROM harmonized.order_items
GROUP BY item_id;