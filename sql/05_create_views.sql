CREATE OR REPLACE VIEW public.vw_order_details_summary AS
SELECT 
    o.order_id,
    o.customer_id,
    r.restaurant_id,
    r.cuisine AS restaurant_cuisine,
    r.city AS restaurant_city,
    o.order_time,
    o.delivery_time,
    o.status
FROM raw.orders AS o
JOIN raw.restaurants AS r ON o.restaurant_id = r.restaurant_id;

--
SELECT 
    restaurant_cuisine,
    COUNT(order_id) AS total_orders
FROM public.vw_order_details_summary
GROUP BY restaurant_cuisine
ORDER BY total_orders DESC;

