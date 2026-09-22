
-- MASTER PROCEDURE
-- Aquí se llaman todos los procedimientos de transformación de datos para cada tabla

CREATE OR REPLACE PROCEDURE automation.sp_transform_all()
LANGUAGE plpgsql
AS $$
BEGIN
    CALL automation.sp_transform_orders_medium();
    CALL automation.sp_transform_restaurants();
    CALL automation.sp_transform_menu_items();
    -- TODO: Agregar otros procedimientos de transformación aquí
END;
$$;