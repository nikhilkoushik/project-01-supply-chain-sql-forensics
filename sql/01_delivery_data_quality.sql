
-- PROJECT 1: SQL FORENSICS ENGINE
-- FILE: 01_delivery_data_quality.sql
-- BUSINESS OBJECTIVE:
-- Detect missing delivery dates and investigate
-- data quality issues in the orders dataset.

-- 1. Missing delivery dates by order status

SELECT
    order_status,
    COUNT(*) AS total_orders,
    COUNT(order_delivered_customer_date) AS with_delivery_date,
    COUNT(*) - COUNT(order_delivered_customer_date)
        AS missing_delivery_date
FROM olist.orders
GROUP BY order_status
ORDER BY missing_delivery_date DESC;


-- 2. Create reusable delivery exception view

CREATE OR REPLACE VIEW olist.v_delivery_date_exceptions AS
SELECT
    order_id,
    customer_id,
    order_status,
    order_delivered_customer_date,
    order_estimated_delivery_date
FROM olist.orders
WHERE order_status = 'delivered'
  AND order_delivered_customer_date IS NULL;


-- 3. Validate the number of exceptions

SELECT
    COUNT(*) AS exception_count
FROM olist.v_delivery_date_exceptions;


-- 4. Check impossible timestamp sequences

SELECT
    COUNT(*) AS total_delivered,

    COUNT(*) FILTER (
        WHERE order_delivered_carrier_date IS NULL
    ) AS missing_carrier_date,

    COUNT(*) FILTER (
        WHERE order_delivered_carrier_date
              < order_purchase_timestamp
    ) AS carrier_before_purchase,

    COUNT(*) FILTER (
        WHERE order_delivered_customer_date
              < order_delivered_carrier_date
    ) AS delivery_before_carrier

FROM olist.orders
WHERE order_status = 'delivered';
