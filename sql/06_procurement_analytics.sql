CREATE OR REPLACE VIEW bpi2019.v_procurement_case_summary AS

SELECT
    e.case_id,
    c.vendor_id,
    c.company,
    c.document_type,
    c.item_category,
    c.item_type,
    c.spend_area,

    COUNT(*) AS total_events,

    MIN(e.event_timestamp) AS first_event,
    MAX(e.event_timestamp) AS last_event,

    ROUND(
        (
            EXTRACT(EPOCH FROM (
                MAX(e.event_timestamp)
                - MIN(e.event_timestamp)
            )) / 86400.0
        )::numeric,
        2
    ) AS case_duration_days,

    COUNT(*) FILTER (
        WHERE e.activity = 'Record Goods Receipt'
    ) AS goods_receipt_count,

    COUNT(*) FILTER (
        WHERE e.activity = 'Record Service Entry Sheet'
    ) AS service_entry_count,

    COUNT(*) FILTER (
        WHERE e.activity = 'Change Quantity'
    ) AS quantity_change_count,

    COUNT(*) FILTER (
        WHERE e.activity = 'Change Price'
    ) AS price_change_count,

    COUNT(*) FILTER (
        WHERE e.activity = 'Cancel Goods Receipt'
    ) AS goods_receipt_cancellation_count,

    COUNT(*) FILTER (
        WHERE e.activity = 'Cancel Invoice Receipt'
    ) AS invoice_receipt_cancellation_count

FROM bpi2019.procurement_events e

JOIN bpi2019.procurement_cases c
    ON e.case_id = c.case_id

GROUP BY
    e.case_id,
    c.vendor_id,
    c.company,
    c.document_type,
    c.item_category,
    c.item_type,
    c.spend_area;



SELECT
    COUNT(*) AS total_cases,

    COUNT(*) FILTER (
        WHERE goods_receipt_count > 1
    ) AS multiple_receipt_cases,

    COUNT(*) FILTER (
        WHERE quantity_change_count > 0
    ) AS cases_with_quantity_changes,

    COUNT(*) FILTER (
        WHERE price_change_count > 0
    ) AS cases_with_price_changes

FROM bpi2019.v_procurement_case_summary;



SELECT
    case_id,
    vendor_id,
    item_category,
    item_type,
    total_events,
    case_duration_days,
    goods_receipt_count,
    service_entry_count,
    quantity_change_count,
    price_change_count
FROM bpi2019.v_procurement_case_summary
WHERE first_event >= '2018-01-01'
  AND last_event < '2020-01-01'
ORDER BY case_duration_days DESC
LIMIT 20;



CREATE OR REPLACE VIEW
bpi2019.v_procurement_investigation_scorecard AS

WITH case_flags AS (
    SELECT
        case_id,
        vendor_id,
        item_category,
        item_type,
        total_events,
        first_event,
        last_event,
        case_duration_days,
        goods_receipt_count,
        service_entry_count,
        quantity_change_count,
        price_change_count,
        goods_receipt_cancellation_count,
        invoice_receipt_cancellation_count,

        CASE
            WHEN case_duration_days > 90 THEN 1
            ELSE 0
        END AS long_duration_flag,

        CASE
            WHEN quantity_change_count > 0
              OR price_change_count > 0
            THEN 1
            ELSE 0
        END AS po_modified_flag,

        CASE
            WHEN goods_receipt_cancellation_count > 0
              OR invoice_receipt_cancellation_count > 0
            THEN 1
            ELSE 0
        END AS cancellation_flag

    FROM bpi2019.v_procurement_case_summary

    WHERE first_event >= '2018-01-01'
      AND last_event < '2020-01-01'
),

scored_cases AS (
    SELECT
        *,
        (
            long_duration_flag
            + po_modified_flag
            + cancellation_flag
        ) AS investigation_score
    FROM case_flags
)

SELECT
    *,
    CASE
        WHEN investigation_score >= 2 THEN 'High'
        WHEN investigation_score = 1 THEN 'Medium'
        ELSE 'Low'
    END AS investigation_priority

FROM scored_cases;


SELECT
    investigation_priority,
    COUNT(*) AS total_cases,

    ROUND(
        100.0 * COUNT(*)
        / SUM(COUNT(*)) OVER (),
        2
    ) AS percentage_of_cases,

    ROUND(
        AVG(case_duration_days),
        2
    ) AS average_duration_days

FROM bpi2019.v_procurement_investigation_scorecard

GROUP BY investigation_priority

ORDER BY
    CASE investigation_priority
        WHEN 'High' THEN 1
        WHEN 'Medium' THEN 2
        ELSE 3
    END;


SELECT
    case_id,
    vendor_id,
    item_type,
    case_duration_days,
    quantity_change_count,
    price_change_count,
    goods_receipt_cancellation_count,
    invoice_receipt_cancellation_count,
    investigation_score,
    investigation_priority

FROM bpi2019.v_procurement_investigation_scorecard

WHERE investigation_priority = 'High'

ORDER BY
    investigation_score DESC,
    case_duration_days DESC,
    case_id

LIMIT 10;
