-- ================================================
-- Apache Iceberg: Snapshot Management Examples
-- ================================================

-- Example 1: View all snapshots for a table
SELECT
    snapshot_id,
    parent_id,
    timestamp_ms,
    operation,
    summary
FROM sap_bdc.finance.general_ledger.snapshots
ORDER BY timestamp_ms DESC
LIMIT 20;

-- Example 2: View detailed snapshot metadata
SELECT
    made_current_at,
    snapshot_id,
    parent_id,
    is_current_ancestor,
    data_files_count,
    total_records_count,
    total_data_size_bytes,
    operation
FROM sap_bdc.sales.orders.snapshots
ORDER BY made_current_at DESC;

-- Example 3: Rollback to previous snapshot
-- Revert table to earlier state after bad data load
CALL spark_catalog.system.rollback_to_snapshot('sap_bdc.finance.general_ledger', 5678901234567890);

-- Example 4: Rollback using timestamp
-- Revert to table state at specific time
CALL spark_catalog.system.rollback_to_timestamp('sap_bdc.sales.orders', TIMESTAMP '2025-01-15 14:30:00');

-- Example 5: Set current snapshot explicitly
-- Advanced snapshot navigation
CALL spark_catalog.system.set_current_snapshot('sap_bdc.hr.employee_records', 8765432109876543);

-- Example 6: Expire old snapshots
-- Clean up snapshots older than 30 days to save metadata storage
CALL spark_catalog.system.expire_snapshots('sap_bdc.sales.orders', TIMESTAMP '2024-12-15 00:00:00');

-- Example 7: Expire snapshots with retention options
-- Keep at least 10 snapshots and retain for minimum 7 days
CALL spark_catalog.system.expire_snapshots(
    table => 'sap_bdc.finance.transactions',
    older_than => TIMESTAMP '2025-01-01 00:00:00',
    retain_last => 10,
    max_concurrent_deletes => 5
);

-- Example 8: View snapshot history with file statistics
SELECT
    committed_at,
    snapshot_id,
    operation,
    summary['added-data-files'] AS files_added,
    summary['deleted-data-files'] AS files_deleted,
    summary['added-records'] AS records_added,
    summary['deleted-records'] AS records_deleted,
    summary['total-data-files'] AS total_files
FROM sap_bdc.supply_chain.deliveries.snapshots
ORDER BY committed_at DESC;

-- Example 9: Create table branch for testing
-- Branch allows isolated changes without affecting main table
CALL spark_catalog.system.create_branch(
    'sap_bdc.finance.general_ledger',
    'test_branch',
    8734629847362 -- starting snapshot ID
);

-- Example 10: Query data from a branch
SELECT *
FROM sap_bdc.finance.general_ledger.branch_test_branch
WHERE account_type = 'REVENUE';

-- Example 11: Create table tag for important snapshots
-- Tag snapshots for auditing or regulatory compliance
CALL spark_catalog.system.create_tag(
    'sap_bdc.finance.general_ledger',
    'year_end_2024',
    8734629847362
);

-- Example 12: Query tagged snapshot
SELECT *
FROM sap_bdc.finance.general_ledger.tag_year_end_2024;

-- Example 13: List all branches and tags
SELECT
    name,
    type,
    snapshot_id,
    max_reference_age_ms
FROM sap_bdc.finance.general_ledger.refs;

-- Example 14: Remove orphan files
-- Clean up data files no longer referenced by any snapshot
CALL spark_catalog.system.remove_orphan_files(
    table => 'sap_bdc.sales.orders',
    older_than => TIMESTAMP '2024-12-01 00:00:00',
    location => 's3://data-lake/sap_bdc/sales/orders/'
);

-- Example 15: Rewrite data files for optimization
-- Compact small files into larger ones for better query performance
CALL spark_catalog.system.rewrite_data_files('sap_bdc.sales.orders');

-- Example 16: Rewrite with filters for specific partitions
CALL spark_catalog.system.rewrite_data_files(
    table => 'sap_bdc.sales.orders',
    where => 'order_date >= "2025-01-01"'
);

-- Example 17: Rewrite manifests
-- Optimize manifest files for faster query planning
CALL spark_catalog.system.rewrite_manifests('sap_bdc.finance.transactions');

-- Example 18: Fast-forward branch to latest
-- Update branch to match current table state
CALL spark_catalog.system.fast_forward(
    'sap_bdc.finance.general_ledger',
    'test_branch',
    'main'
);

-- Example 19: Cherry-pick snapshot to branch
-- Apply specific changes to a branch
CALL spark_catalog.system.cherrypick_snapshot(
    'sap_bdc.hr.employee_records',
    8765432109876543
);

-- Example 20: View metadata for snapshot lifecycle
-- Understand snapshot retention and cleanup status
WITH snapshot_age AS (
    SELECT
        snapshot_id,
        committed_at,
        operation,
        DATEDIFF(CURRENT_DATE, DATE(committed_at)) AS age_days,
        CASE
            WHEN is_current_ancestor THEN 'Ancestor'
            ELSE 'Orphan Candidate'
        END AS snapshot_status
    FROM sap_bdc.sales.orders.snapshots
)
SELECT
    snapshot_status,
    COUNT(*) AS snapshot_count,
    AVG(age_days) AS avg_age_days,
    MAX(age_days) AS oldest_age_days
FROM snapshot_age
GROUP BY snapshot_status;

-- Example 21: Audit snapshot operations
-- Track who made changes and when
SELECT
    committed_at,
    snapshot_id,
    operation,
    summary['spark.app.id'] AS application_id,
    summary['committed-at'] AS commit_timestamp,
    summary['total-records'] AS record_count
FROM sap_bdc.finance.general_ledger.snapshots
WHERE DATE(committed_at) = CURRENT_DATE
ORDER BY committed_at DESC;

-- Example 22: Compare snapshots
-- Identify differences between two snapshots
WITH snapshot1 AS (
    SELECT * FROM sap_bdc.sales.orders
    VERSION AS OF 8734629847362
),
snapshot2 AS (
    SELECT * FROM sap_bdc.sales.orders
    VERSION AS OF 8734629999999
)
SELECT 'Added' AS change_type, * FROM snapshot2
WHERE order_id NOT IN (SELECT order_id FROM snapshot1)
UNION ALL
SELECT 'Removed' AS change_type, * FROM snapshot1
WHERE order_id NOT IN (SELECT order_id FROM snapshot2);

-- Example 23: Monitor snapshot growth
-- Track snapshot accumulation over time
SELECT
    DATE(committed_at) AS snapshot_date,
    COUNT(*) AS snapshots_created,
    SUM(CAST(summary['added-records'] AS BIGINT)) AS total_records_added,
    SUM(CAST(summary['added-data-files'] AS INT)) AS total_files_added
FROM sap_bdc.supply_chain.inventory.snapshots
WHERE committed_at >= CURRENT_DATE - INTERVAL 30 DAYS
GROUP BY DATE(committed_at)
ORDER BY snapshot_date DESC;

-- Example 24: Identify large snapshots for cleanup
-- Find snapshots consuming significant storage
SELECT
    snapshot_id,
    committed_at,
    operation,
    ROUND(total_data_size_bytes / 1024 / 1024 / 1024, 2) AS size_gb,
    total_records_count
FROM sap_bdc.sales.orders.snapshots
WHERE total_data_size_bytes > 10 * 1024 * 1024 * 1024 -- > 10 GB
ORDER BY total_data_size_bytes DESC;

-- Example 25: Restore table after accidental deletion
-- Recover from DROP TABLE or major data loss
-- First, check the last valid snapshot
SELECT snapshot_id, committed_at, operation
FROM sap_bdc.finance.general_ledger.snapshots
ORDER BY committed_at DESC
LIMIT 5;

-- Then rollback to restore
CALL spark_catalog.system.rollback_to_snapshot(
    'sap_bdc.finance.general_ledger',
    8734629847362
);
