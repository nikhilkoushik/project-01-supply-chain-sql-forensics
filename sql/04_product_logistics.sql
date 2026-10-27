
-- PROJECT 1: SUPPLY CHAIN SQL FORENSICS ENGINE
-- FILE: 04_product_logistics.sql
-- DATASET: Olist Brazilian E-Commerce
--
-- BUSINESS OBJECTIVE:
-- Investigate product-category delivery performance,
-- recorded order weight, product volume,
-- freight charges, and logistics reliability.
--
-- LIMITATIONS:
-- Category association does not establish causation.
-- Product weights and volumes exclude packaging.
-- Multi-category orders appear in multiple categories.

-- VIEW 1: ONE ROW PER ORDER PER CATEGORY

CREATE OR REPLACE VIEW olist.v_order_categories AS
SELECT DISTINCT
    i.order_id,
    COALESCE(
        p.product_category_name,
        'unknown'
    ) AS product_category

FROM olist.order_items AS i

INNER JOIN olist.products AS p
    ON i.product_id = p.product_id;



-- VIEW 2: ORDER-LEVEL PRODUCT WEIGHT

CREATE OR REPLACE VIEW olist.v_order_weight AS
SELECT
    i.order_id,

    COUNT(*) AS total_items,

    SUM(p.product_weight_g) AS total_weight_g,

    COUNT(*) FILTER (
        WHERE p.product_weight_g IS NULL
    ) AS items_missing_weight

FROM olist.order_items AS i

INNER JOIN olist.products AS p
    ON i.product_id = p.product_id

GROUP BY i.order_id;


-- VIEW 3: ORDER-LEVEL PHYSICAL LOGISTICS

CREATE OR REPLACE VIEW olist.v_order_logistics AS
SELECT
    i.order_id,

    COUNT(*) AS item_count,

    SUM(p.product_weight_g) AS total_weight_g,

    SUM(
        p.product_length_cm
        * p.product_height_cm
        * p.product_width_cm
    ) AS total_product_volume_cm3,

    SUM(i.freight_value) AS freight_total,

    SUM(i.price) AS product_value,

    COUNT(*) FILTER (
        WHERE p.product_weight_g IS NULL
           OR p.product_length_cm IS NULL
           OR p.product_height_cm IS NULL
           OR p.product_width_cm IS NULL
    ) AS items_missing_physical_data

FROM olist.order_items AS i

INNER JOIN olist.products AS p
    ON i.product_id = p.product_id

GROUP BY i.order_id;

-- VALIDATION 1: PRODUCT RELATIONSHIP QUALITY

SELECT
    COUNT(*) AS orphan_product_items
FROM olist.order_items AS i

LEFT JOIN olist.products AS p
    ON i.product_id = p.product_id

WHERE p.product_id IS NULL;


-- VALIDATION 2: ORDER WEIGHT VIEW

SELECT
    COUNT(*) AS total_orders,

    COUNT(*) FILTER (
        WHERE items_missing_weight > 0
    ) AS orders_with_missing_weight

FROM olist.v_order_weight;


-- VALIDATION 3: LOGISTICS VIEW

SELECT
    COUNT(*) AS total_orders,

    COUNT(*) FILTER (
        WHERE items_missing_physical_data > 0
    ) AS incomplete_orders,

    ROUND(
        AVG(freight_total),
        2
    ) AS avg_freight_per_order

FROM olist.v_order_logistics;
