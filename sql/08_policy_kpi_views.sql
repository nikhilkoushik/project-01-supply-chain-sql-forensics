
-- Project 1: Supply Chain SQL Forensics
-- Reusable Olist seller-order policy KPI
-- Historical what-if analysis using simulated policies

CREATE OR REPLACE VIEW olist.v_seller_order_policy_kpi AS

WITH seller_order_handoffs AS (
    SELECT
        i.seller_id,
        i.order_id,
        MIN(i.shipping_limit_date) AS shipping_deadline,
        o.order_delivered_carrier_date AS carrier_handoff
    FROM olist.order_items i
    JOIN olist.orders o
        ON i.order_id = o.order_id
    WHERE o.order_delivered_carrier_date IS NOT NULL
      AND i.shipping_limit_date IS NOT NULL
    GROUP BY
        i.seller_id,
        i.order_id,
        o.order_delivered_carrier_date
)

SELECT
    COUNT(*) AS eligible_seller_orders,

    COUNT(*) FILTER (
        WHERE carrier_handoff <= shipping_deadline
    ) AS on_time_seller_orders,

    COUNT(*) FILTER (
        WHERE carrier_handoff > shipping_deadline
    ) AS late_seller_orders,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE carrier_handoff <= shipping_deadline
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS on_time_percentage

FROM seller_order_handoffs;

-- Verification
SELECT *
FROM olist.v_seller_order_policy_kpi;


-- =====================================================
-- BPI 2019: Standard Procurement First Receipt Policy
-- Simulated company policy classification: STD_MATERIAL
-- =====================================================

CREATE OR REPLACE VIEW bpi2019.v_standard_first_receipt_policy AS

WITH standard_cases AS (
    SELECT
        case_id,
        item_type,
        item_category
    FROM bpi2019.procurement_cases
    WHERE item_type = 'Standard'
),

po_dates AS (
    SELECT
        e.case_id,
        MIN(e.event_timestamp) AS po_created_at
    FROM bpi2019.procurement_events e
    JOIN standard_cases c
        ON e.case_id = c.case_id
    WHERE e.activity = 'Create Purchase Order Item'
    GROUP BY e.case_id
),

first_receipts AS (
    SELECT
        e.case_id,
        MIN(e.event_timestamp) AS first_gr_at
    FROM bpi2019.procurement_events e
    JOIN po_dates p
        ON e.case_id = p.case_id
    WHERE e.activity = 'Record Goods Receipt'
      AND e.event_timestamp >= p.po_created_at
    GROUP BY e.case_id
)

SELECT
    c.case_id,
    c.item_type,
    c.item_category,
    'STD_MATERIAL'::text AS policy_category,

    p.po_created_at,
    g.first_gr_at,

    CASE
        WHEN p.po_created_at IS NULL
            THEN 'missing_po_creation'
        WHEN g.first_gr_at IS NULL
            THEN 'missing_first_receipt'
        ELSE 'valid'
    END AS evidence_status,

    CASE
        WHEN p.po_created_at IS NOT NULL
         AND g.first_gr_at IS NOT NULL
        THEN ROUND(
            (
                EXTRACT(
                    EPOCH FROM (g.first_gr_at - p.po_created_at)
                ) / 86400.0
            )::numeric,
            4
        )
        ELSE NULL
    END AS first_receipt_lead_days

FROM standard_cases c
LEFT JOIN po_dates p
    ON c.case_id = p.case_id
LEFT JOIN first_receipts g
    ON c.case_id = g.case_id;
