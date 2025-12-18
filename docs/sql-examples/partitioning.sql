-- =================================================
-- Apache Iceberg: Partitioning Strategy Examples
-- =================================================

-- Example 1: Create table with hidden partitioning by date
-- Users query by order_date, Iceberg handles partitioning automatically
CREATE TABLE sap_bdc.sales.orders_partitioned (
    order_id STRING,
    customer_id STRING,
    order_date DATE,
    order_amount DECIMAL(18,2),
    status STRING
)
USING iceberg
PARTITIONED BY (days(order_date));

-- Example 2: Partition by year and month
CREATE TABLE sap_bdc.finance.transactions_monthly (
    transaction_id STRING,
    account_id STRING,
    transaction_date TIMESTAMP,
    amount DECIMAL(18,2),
    currency STRING
)
USING iceberg
PARTITIONED BY (years(transaction_date), months(transaction_date));

-- Example 3: Partition by hour for high-frequency data
CREATE TABLE sap_bdc.iot.sensor_readings (
    sensor_id STRING,
    reading_timestamp TIMESTAMP,
    temperature DOUBLE,
    pressure DOUBLE,
    humidity DOUBLE
)
USING iceberg
PARTITIONED BY (hours(reading_timestamp));

-- Example 4: Partition by bucket (hash partitioning)
-- Evenly distribute data across partitions
CREATE TABLE sap_bdc.sales.customers_distributed (
    customer_id STRING,
    customer_name STRING,
    region STRING,
    created_at TIMESTAMP
)
USING iceberg
PARTITIONED BY (bucket(16, customer_id));

-- Example 5: Partition by truncated string values
-- Group by first N characters
CREATE TABLE sap_bdc.products.product_catalog (
    product_id STRING,
    product_name STRING,
    category STRING,
    created_date DATE
)
USING iceberg
PARTITIONED BY (truncate(2, category));

-- Example 6: Multi-column partitioning
-- Partition by region and date for optimal query performance
CREATE TABLE sap_bdc.sales.regional_sales (
    sale_id STRING,
    region STRING,
    sale_date DATE,
    amount DECIMAL(18,2),
    product_id STRING
)
USING iceberg
PARTITIONED BY (region, days(sale_date));

-- Example 7: Query partitioned table (no partition predicates needed)
-- Iceberg automatically prunes partitions
SELECT
    order_id,
    customer_id,
    order_amount
FROM sap_bdc.sales.orders_partitioned
WHERE order_date BETWEEN '2025-01-01' AND '2025-01-31';

-- Example 8: View table partitioning scheme
DESCRIBE EXTENDED sap_bdc.sales.orders_partitioned;

-- Example 9: View partition statistics
SELECT
    partition,
    record_count,
    file_count,
    total_data_file_size_in_bytes
FROM sap_bdc.sales.orders_partitioned.partitions
ORDER BY partition DESC
LIMIT 100;

-- Example 10: Evolve partition spec (add new partition field)
-- Iceberg allows changing partitioning without rewriting data
ALTER TABLE sap_bdc.sales.orders_partitioned
ADD PARTITION FIELD bucket(8, customer_id);

-- Example 11: Remove partition field
ALTER TABLE sap_bdc.sales.orders_partitioned
DROP PARTITION FIELD days(order_date);

-- Example 12: Replace partition spec entirely
ALTER TABLE sap_bdc.sales.regional_sales
REPLACE PARTITION FIELD days(sale_date) WITH months(sale_date);

-- Example 13: View partition evolution history
SELECT
    spec_id,
    fields
FROM sap_bdc.sales.orders_partitioned.partition_specs
ORDER BY spec_id;

-- Example 14: Query specific partitions using metadata
SELECT *
FROM sap_bdc.sales.orders_partitioned
WHERE order_date_day = '2025-01-15';

-- Example 15: Optimize queries with partition pruning
-- Iceberg automatically skips irrelevant partitions
SELECT
    COUNT(*) AS order_count,
    SUM(order_amount) AS total_amount
FROM sap_bdc.sales.orders_partitioned
WHERE order_date >= '2025-01-01'
  AND order_date < '2025-02-01'
  AND status = 'COMPLETED';

-- Example 16: Create table partitioned by derived values
-- Partition by fiscal period instead of calendar date
CREATE TABLE sap_bdc.finance.fiscal_transactions (
    transaction_id STRING,
    transaction_date DATE,
    fiscal_year INT,
    fiscal_quarter INT,
    amount DECIMAL(18,2)
)
USING iceberg
PARTITIONED BY (fiscal_year, fiscal_quarter);

-- Example 17: Identity partitioning (no transformation)
-- Use actual column values as partition keys
CREATE TABLE sap_bdc.sales.orders_by_region (
    order_id STRING,
    region STRING,
    order_date DATE,
    amount DECIMAL(18,2)
)
USING iceberg
PARTITIONED BY (region);

-- Example 18: View files within specific partitions
SELECT
    file_path,
    file_format,
    record_count,
    file_size_in_bytes,
    partition
FROM sap_bdc.sales.orders_partitioned.files
WHERE partition.order_date_day >= '2025-01-01'
ORDER BY partition.order_date_day DESC;

-- Example 19: Compact specific partitions
-- Optimize file layout for frequently queried partitions
CALL spark_catalog.system.rewrite_data_files(
    table => 'sap_bdc.sales.orders_partitioned',
    where => 'order_date >= "2025-01-01" AND order_date < "2025-02-01"',
    options => map('target-file-size-bytes', '536870912') -- 512 MB
);

-- Example 20: Sort data within partitions
-- Create table with sorted data for better compression and query performance
CREATE TABLE sap_bdc.sales.orders_sorted (
    order_id STRING,
    customer_id STRING,
    order_date DATE,
    order_amount DECIMAL(18,2),
    status STRING
)
USING iceberg
PARTITIONED BY (days(order_date))
TBLPROPERTIES (
    'write.distribution-mode' = 'hash',
    'write.target-file-size-bytes' = '536870912'
)
SORTED BY (customer_id, order_id);

-- Example 21: Partition by SAP-specific fields
-- Partition SAP data by company code and fiscal period
CREATE TABLE sap_bdc.finance.sap_general_ledger (
    document_number STRING,
    company_code STRING,
    fiscal_year INT,
    fiscal_period INT,
    posting_date DATE,
    account_number STRING,
    amount DECIMAL(18,2),
    currency STRING
)
USING iceberg
PARTITIONED BY (company_code, fiscal_year, fiscal_period);

-- Example 22: Query with partition column metadata
SELECT
    COUNT(*) AS record_count,
    order_date,
    partition.order_date_day AS partition_value
FROM sap_bdc.sales.orders_partitioned
GROUP BY order_date, partition.order_date_day;

-- Example 23: Analyze partition skew
-- Identify unbalanced partitions
SELECT
    partition,
    record_count,
    file_count,
    ROUND(total_data_file_size_in_bytes / 1024 / 1024, 2) AS size_mb
FROM sap_bdc.sales.orders_partitioned.partitions
WHERE record_count > 0
ORDER BY record_count DESC
LIMIT 20;

-- Example 24: Partition evolution for SAP data products
-- Start with daily partitions, evolve to monthly as data matures
-- Initial state: daily partitioning
ALTER TABLE sap_bdc.sales.orders_partitioned
ADD PARTITION FIELD months(order_date);

-- Future queries benefit from both partition schemes
SELECT
    order_date,
    COUNT(*) AS order_count
FROM sap_bdc.sales.orders_partitioned
WHERE order_date >= '2024-01-01'
GROUP BY order_date;

-- Example 25: Hidden partitioning benefits
-- Users don't need to know partitioning scheme
-- Both queries are optimized automatically:

-- Query 1: Filter by exact date
SELECT * FROM sap_bdc.sales.orders_partitioned
WHERE order_date = '2025-01-15';

-- Query 2: Filter by date range
SELECT * FROM sap_bdc.sales.orders_partitioned
WHERE order_date BETWEEN '2025-01-01' AND '2025-01-31';

-- Query 3: Filter by timestamp (even though partitioned by date)
SELECT * FROM sap_bdc.iot.sensor_readings
WHERE reading_timestamp >= '2025-01-15 14:30:00'
  AND reading_timestamp < '2025-01-15 15:00:00';

-- Iceberg automatically prunes partitions in all cases
