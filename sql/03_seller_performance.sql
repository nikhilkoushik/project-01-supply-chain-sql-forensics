
-- PROJECT 1: SQL FORENSICS ENGINE
-- FILE: 03_seller_performance.sql
-- DATASET: Olist Brazilian E-Commerce
--
-- BUSINESS OBJECTIVE:
-- Analyze seller-associated delivery delays,
-- shipping deadline performance,
-- and investigation priorities.
--
-- IMPORTANT:
-- Seller association does not prove responsibility
-- for late customer deliveries.


-- ============================================
-- PROJECT 1: SUPPLY CHAIN SQL FORENSICS ENGINE
-- FILE: 03_seller_performance.sql
-- DATASET: Olist Brazilian E-Commerce
-- ============================================

-- VIEW 1: SELLER-ORDER RELATIONSHIPS
-- One row per seller and order.
-- Prevents counting multiple items from the
-- same seller in one order as multiple orders.

CREATE OR REPLACE VIEW olist.v_seller_orders AS
SELECT DISTINCT
    seller_id,
    order_id
FROM olist.order_items;


-- ============================================
-- VIEW 2: SELLER SHIPPING DEADLINE PERFORMANCE
-- Compares item shipping deadlines with the
-- recorded order-level carrier handoff date.
-- This is a proxy, not confirmed seller fault.
-- ============================================

CREATE OR REPLACE VIEW olist.v_seller_shipping_performance AS
SELECT
    i.seller_id,

    COUNT(*) AS analyzed_items,

    COUNT(*) FILTER (
        WHERE o.order_delivered_carrier_date
              > i.shipping_limit_date
    ) AS after_deadline_items,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE o.order_delivered_carrier_date
                  > i.shipping_limit_date
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS after_deadline_percentage

FROM olist.order_items AS i

INNER JOIN olist.orders AS o
    ON i.order_id = o.order_id

WHERE o.order_status = 'delivered'
  AND o.order_delivered_carrier_date IS NOT NULL
  AND i.shipping_limit_date IS NOT NULL

GROUP BY i.seller_id;


-- ============================================
-- VIEW 3: SELLER-ASSOCIATED DELIVERY PERFORMANCE
-- Measures customer late-delivery outcomes
-- associated with each seller.
-- Does not prove seller responsibility.
-- ============================================

CREATE OR REPLACE VIEW olist.v_seller_delivery_performance AS
SELECT
    s.seller_id,

    COUNT(*) AS delivered_orders,

    COUNT(*) FILTER (
        WHERE o.order_delivered_customer_date::DATE
              > o.order_estimated_delivery_date::DATE
    ) AS late_orders,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE o.order_delivered_customer_date::DATE
                  > o.order_estimated_delivery_date::DATE
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS late_order_percentage

FROM olist.v_seller_orders AS s

INNER JOIN olist.orders AS o
    ON s.order_id = o.order_id

WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
  AND o.order_estimated_delivery_date IS NOT NULL

GROUP BY s.seller_id;


-- ============================================
-- VIEW 4: COMBINED SELLER SCORECARD
-- Combines the two performance indicators.
-- Applies exploratory business thresholds.
-- ============================================

CREATE OR REPLACE VIEW olist.v_seller_scorecard AS
SELECT
    d.seller_id,
    d.delivered_orders,
    d.late_orders,
    d.late_order_percentage,
    s.analyzed_items,
    s.after_deadline_items,
    s.after_deadline_percentage,

    CASE
        WHEN d.late_order_percentage >= 15
         AND s.after_deadline_percentage >= 20
        THEN 'High'

        WHEN d.late_order_percentage >= 15
          OR s.after_deadline_percentage >= 20
        THEN 'Medium'

        ELSE 'Low'
    END AS investigation_priority

FROM olist.v_seller_delivery_performance AS d

INNER JOIN olist.v_seller_shipping_performance AS s
    ON d.seller_id = s.seller_id

WHERE d.delivered_orders >= 30
  AND s.analyzed_items >= 30;


-- ============================================
-- VALIDATION 1: SELLER PRIORITY COUNTS
-- ============================================

SELECT
    investigation_priority,
    COUNT(*) AS seller_count
FROM olist.v_seller_scorecard
GROUP BY investigation_priority
ORDER BY
    CASE investigation_priority
        WHEN 'High' THEN 1
        WHEN 'Medium' THEN 2
        ELSE 3
    END;


-- ============================================
-- VALIDATION 2: SHARE OF LATE ASSOCIATIONS
-- ============================================

WITH priority_summary AS (
    SELECT
        investigation_priority,
        COUNT(*) AS seller_count,
        SUM(late_orders) AS late_associations
    FROM olist.v_seller_scorecard
    GROUP BY investigation_priority
)

SELECT
    investigation_priority,
    seller_count,
    late_associations,

    ROUND(
        100.0 * late_associations
        / NULLIF(
            SUM(late_associations) OVER (),
            0
        ),
        2
    ) AS share_of_late_associations_pct

FROM priority_summary
ORDER BY late_associations DESC;
