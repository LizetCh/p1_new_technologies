---View: Customers by city

CREATE OR REPLACE VIEW analytics.vw_customers_by_city AS
SELECT
    city,
    COUNT(*) AS total_customers
FROM harmonized.customers
GROUP BY city
ORDER BY total_customers DESC;

--To call the view
SELECT * FROM analytics.vw_customers_by_city;


---View: Customer signups by month
CREATE OR REPLACE VIEW analytics.vw_customer_signups_by_month AS
SELECT
    EXTRACT(YEAR FROM signup_date)::INT AS signup_year,
    EXTRACT(MONTH FROM signup_date)::INT AS signup_month_number,
    TRIM(TO_CHAR(signup_date, 'Month')) AS signup_month_name,
    COUNT(*) AS total_signups
FROM harmonized.customers
GROUP BY
    EXTRACT(YEAR FROM signup_date),
    EXTRACT(MONTH FROM signup_date),
    TRIM(TO_CHAR(signup_date, 'Month'))
ORDER BY signup_year, signup_month_number;

--To call the view
SELECT * FROM analytics.vw_customer_signups_by_month;


SELECT * FROM analytics.vw_customers_by_city;
SELECT * FROM analytics.vw_customer_signups_by_month;

