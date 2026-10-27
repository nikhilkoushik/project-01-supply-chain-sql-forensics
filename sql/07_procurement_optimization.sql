
-- ==============================================
-- PROJECT 1: SQL FORENSICS ENGINE
-- Procurement Query Optimization
-- ==============================================

-- Inspect existing indexes
SELECT
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'bpi2019'
ORDER BY tablename, indexname;


-- Update table statistics
ANALYZE bpi2019.procurement_cases;
ANALYZE bpi2019.procurement_events;


-- BASELINE QUERY
-- For an actual before-index benchmark,
-- run this only before creating the index.

EXPLAIN (ANALYZE, BUFFERS)
SELECT
    case_id,
    activity,
    event_timestamp
FROM bpi2019.procurement_events
WHERE activity = 'Cancel Goods Receipt'
ORDER BY event_timestamp DESC
LIMIT 100;


-- Targeted partial index
CREATE INDEX IF NOT EXISTS idx_bpi_cancel_gr_recent
ON bpi2019.procurement_events (
    event_timestamp DESC
)
WHERE activity = 'Cancel Goods Receipt';


-- AFTER-INDEX QUERY
EXPLAIN (ANALYZE, BUFFERS)
SELECT
    case_id,
    activity,
    event_timestamp
FROM bpi2019.procurement_events
WHERE activity = 'Cancel Goods Receipt'
ORDER BY event_timestamp DESC
LIMIT 100;


-- Observed local benchmark:
-- Before: 692.982 ms
-- After:    4.235 ms
-- Speedup: approximately 163.6x
--
-- One-run comparison, not a repeatable
-- production performance guarantee.
