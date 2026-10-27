
-- PROJECT 1: SQL FORENSICS ENGINE
-- FILE: 02_regional_delivery_performance.sql
-- BUSINESS OBJECTIVE:
-- Analyze regional delivery performance,
-- delivery delays and promised delivery windows.

-- 1. Create reusable state delivery KPI view

CREATE OR REPLACE VIEW olist.v_state_delivery_performance AS
SELECT
    c.customer_state,

    COUNT(*) AS total_deliveries,

    COUNT(*) FILTER (
        WHERE o.order_delivered_customer_date::DATE
              <= o.order_estimated_delivery_date::DATE
    ) AS on_time_deliveries,

    COUNT(*) FILTER (
        WHERE o.order_delivered_customer_date::DATE
              > o.order_estimated_delivery_date::DATE
    ) AS late_deliveries,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE o.order_delivered_customer_date::DATE
                  > o.order_estimated_delivery_date::DATE
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS late_delivery_percentage,

    ROUND(
        AVG(
            o.order_estimated_delivery_date::DATE
            - o.order_purchase_timestamp::DATE
        ),
        2
    ) AS avg_promised_days,

    ROUND(
        AVG(
            o.order_delivered_customer_date::DATE
            - o.order_purchase_timestamp::DATE
        ),
        2
    ) AS avg_actual_days,

    ROUND(
        AVG(
            o.order_delivered_customer_date::DATE
            - o.order_estimated_delivery_date::DATE
        ),
        2
    ) AS avg_days_early_or_late

FROM olist.orders AS o
INNER JOIN olist.customers AS c
    ON o.customer_id = c.customer_id

WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
  AND o.order_estimated_delivery_date IS NOT NULL
  AND o.order_purchase_timestamp IS NOT NULL

GROUP BY c.customer_state;


-- 2. Rank states with at least 300 deliveries

SELECT
    customer_state,
    total_deliveries,
    late_deliveries,
    late_delivery_percentage,

    DENSE_RANK() OVER (
        ORDER BY late_delivery_percentage DESC
    ) AS delay_rank

FROM olist.v_state_delivery_performance

WHERE total_deliveries >= 300

ORDER BY delay_rank, customer_state;


-- 3. Validate the total delivery counts

SELECT
    SUM(total_deliveries) AS total_deliveries,
    SUM(on_time_deliveries) AS on_time_deliveries,
    SUM(late_deliveries) AS late_deliveries

FROM olist.v_state_delivery_performance;
