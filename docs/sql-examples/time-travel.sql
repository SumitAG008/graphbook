-- ============================================
-- Apache Iceberg: Time Travel Query Examples
-- ============================================

-- Example 1: Query table as of a specific timestamp
-- Useful for auditing and compliance scenarios
SELECT *
FROM sap_bdc.finance.general_ledger
FOR SYSTEM_TIME AS OF '2025-01-01 00:00:00';

-- Example 2: Query using snapshot ID
-- Provides exact point-in-time consistency
SELECT *
FROM sap_bdc.finance.general_ledger
VERSION AS OF 8734629847362;

-- Example 3: Compare current vs historical data
-- Identify changes between two points in time
WITH current_data AS (
    SELECT account_id, balance, last_updated
    FROM sap_bdc.finance.general_ledger
),
historical_data AS (
    SELECT account_id, balance, last_updated
    FROM sap_bdc.finance.general_ledger
    FOR SYSTEM_TIME AS OF '2024-12-31 23:59:59'
)
SELECT
    c.account_id,
    h.balance AS previous_balance,
    c.balance AS current_balance,
    c.balance - h.balance AS balance_change
FROM current_data c
INNER JOIN historical_data h ON c.account_id = h.account_id
WHERE c.balance != h.balance;

-- Example 4: Query data from 7 days ago
-- Relative time travel for periodic comparisons
SELECT *
FROM sap_bdc.hr.employee_records
FOR SYSTEM_TIME AS OF CURRENT_TIMESTAMP - INTERVAL 7 DAYS;

-- Example 5: Audit trail - see all versions of a specific record
SELECT
    employee_id,
    employee_name,
    department,
    salary,
    _iceberg_snapshot_id AS snapshot_id,
    _iceberg_commit_time AS commit_time
FROM sap_bdc.hr.employee_records
FOR SYSTEM_TIME AS OF '2025-01-01'
WHERE employee_id = 'EMP12345'
UNION ALL
SELECT
    employee_id,
    employee_name,
    department,
    salary,
    _iceberg_snapshot_id,
    _iceberg_commit_time
FROM sap_bdc.hr.employee_records
WHERE employee_id = 'EMP12345';

-- Example 6: Financial reconciliation with time travel
-- Compare month-end balances across periods
SELECT
    account_id,
    account_name,
    SUM(CASE
        WHEN transaction_date BETWEEN '2024-11-01' AND '2024-11-30'
        THEN amount ELSE 0 END) AS nov_balance,
    SUM(CASE
        WHEN transaction_date BETWEEN '2024-12-01' AND '2024-12-31'
        THEN amount ELSE 0 END) AS dec_balance
FROM sap_bdc.finance.transactions
FOR SYSTEM_TIME AS OF '2024-12-31 23:59:59'
GROUP BY account_id, account_name;

-- Example 7: View all available snapshots for a table
-- List all snapshots with timestamps and operations
SELECT
    snapshot_id,
    committed_at,
    operation,
    summary
FROM sap_bdc.finance.general_ledger.snapshots
ORDER BY committed_at DESC;

-- Example 8: Time travel with JOIN operations
-- Combine historical data from multiple tables
SELECT
    o.order_id,
    o.order_date,
    o.total_amount,
    c.customer_name,
    c.customer_segment
FROM sap_bdc.sales.orders FOR SYSTEM_TIME AS OF '2024-12-31' o
INNER JOIN sap_bdc.sales.customers FOR SYSTEM_TIME AS OF '2024-12-31' c
    ON o.customer_id = c.customer_id
WHERE o.order_date BETWEEN '2024-12-01' AND '2024-12-31';

-- Example 9: Incremental processing using time travel
-- Process only new records since last run
SELECT *
FROM sap_bdc.supply_chain.deliveries
WHERE _iceberg_commit_time > (
    SELECT MAX(last_processed_time)
    FROM processing_metadata.job_runs
    WHERE job_name = 'delivery_processing'
);

-- Example 10: Point-in-time reporting with aggregations
-- Generate reports as they would have appeared at a specific time
SELECT
    region,
    product_category,
    COUNT(DISTINCT order_id) AS order_count,
    SUM(order_amount) AS total_revenue,
    AVG(order_amount) AS avg_order_value
FROM sap_bdc.sales.orders
FOR SYSTEM_TIME AS OF '2024-12-31 23:59:59'
WHERE order_date >= '2024-01-01'
GROUP BY region, product_category
ORDER BY total_revenue DESC;
