
-- ============================================
-- PROJECT 1: SUPPLY CHAIN SQL FORENSICS
-- FILE: 05_sql_optimization.sql
-- PURPOSE: Indexing and query performance
-- ============================================

-- LESSON 32: CUSTOMER ID LOOKUP
-- Establish a baseline before adding the index.

EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM olist.orders
WHERE customer_id = (
    SELECT customer_id
    FROM olist.orders
    LIMIT 1
);


-- Create customer ID index on orders.
CREATE INDEX IF NOT EXISTS idx_orders_customer_id
ON olist.orders(customer_id);


-- Repeat lookup to inspect index usage.
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM olist.orders
WHERE customer_id = (
    SELECT customer_id
    FROM olist.orders
    LIMIT 1
);


-- LESSON 33: REGIONAL JOIN
-- Refresh statistics.

ANALYZE olist.orders;
ANALYZE olist.customers;


-- Inspect delivered orders for Sao Paulo.
EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*) AS delivered_orders
FROM olist.orders AS o
JOIN olist.customers AS c
    ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered'
  AND c.customer_state = 'SP';


-- Review existing indexes.
SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'olist'
  AND tablename IN ('orders', 'customers')
ORDER BY tablename, indexname;


-- LESSON 34: STATE INDEX
-- Test selectivity for common and rare states.

CREATE INDEX IF NOT EXISTS idx_customers_state
ON olist.customers(customer_state);

ANALYZE olist.customers;


-- Common state: Sao Paulo
EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*) AS delivered_orders
FROM olist.orders AS o
JOIN olist.customers AS c
    ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered'
  AND c.customer_state = 'SP';


-- More selective state: Roraima
EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*) AS delivered_orders
FROM olist.orders AS o
JOIN olist.customers AS c
    ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered'
  AND c.customer_state = 'RR';
