-- Asegurar que el esquema raw exista
CREATE SCHEMA IF NOT EXISTS raw;

-- Eliminar la tabla si ya existe para recrearla limpia
DROP TABLE IF EXISTS raw.restaurants;

-- Crear la tabla raw.restaurants con sus tipos de datos correctos
CREATE TABLE raw.restaurants (
    restaurant_id VARCHAR(50) PRIMARY KEY,
    cuisine VARCHAR(100),
    city VARCHAR(100),
    rating NUMERIC(3, 2)
);