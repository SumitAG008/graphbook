-- ================================================
-- Apache Iceberg: Schema Evolution Query Examples
-- ================================================

-- Example 1: Add a new column to existing table
-- No data rewrite required - Iceberg handles this efficiently
ALTER TABLE sap_bdc.hr.employee_records
ADD COLUMN remote_work_eligible BOOLEAN;

-- Example 2: Add multiple columns at once
ALTER TABLE sap_bdc.sales.orders
ADD COLUMNS (
    discount_code STRING,
    loyalty_points_earned INT,
    shipping_carrier STRING
);

-- Example 3: Rename a column
-- Preserves existing data without rewriting files
ALTER TABLE sap_bdc.finance.general_ledger
RENAME COLUMN acc_num TO account_number;

-- Example 4: Drop a column
-- Column is removed from schema but data files remain unchanged
ALTER TABLE sap_bdc.sales.customers
DROP COLUMN legacy_customer_id;

-- Example 5: Change column data type (widening)
-- Safe operations like INT to BIGINT don't require rewrites
ALTER TABLE sap_bdc.supply_chain.inventory
ALTER COLUMN quantity TYPE BIGINT;

-- Example 6: Update column comment/documentation
ALTER TABLE sap_bdc.hr.employee_records
ALTER COLUMN employee_id COMMENT 'Unique employee identifier from SAP SuccessFactors';

-- Example 7: Reorder columns (cosmetic change)
-- Doesn't affect data storage, only schema presentation
ALTER TABLE sap_bdc.sales.products
ALTER COLUMN product_name FIRST;

ALTER TABLE sap_bdc.sales.products
ALTER COLUMN product_id AFTER product_name;

-- Example 8: Set default value for new column
-- Applies to future inserts, existing rows get NULL
ALTER TABLE sap_bdc.sales.orders
ADD COLUMN order_source STRING DEFAULT 'WEB';

-- Example 9: Schema evolution with backward compatibility
-- Query old and new schema versions seamlessly
SELECT
    order_id,
    order_date,
    customer_id,
    total_amount,
    -- New columns may be NULL for historical data
    COALESCE(discount_code, 'NONE') AS discount_code,
    COALESCE(loyalty_points_earned, 0) AS loyalty_points
FROM sap_bdc.sales.orders;

-- Example 10: View table schema history
-- Track all schema changes over time
SELECT
    schema_id,
    timestamp,
    schema
FROM sap_bdc.sales.orders.schemas
ORDER BY timestamp DESC;

-- Example 11: Add nested struct column
-- Support for complex data types
ALTER TABLE sap_bdc.sales.customers
ADD COLUMN address STRUCT<
    street: STRING,
    city: STRING,
    state: STRING,
    postal_code: STRING,
    country: STRING
>;

-- Example 12: Add array column for multi-valued attributes
ALTER TABLE sap_bdc.sales.products
ADD COLUMN tags ARRAY<STRING>;

-- Example 13: Safe schema evolution pattern
-- Always check current schema before making changes
DESCRIBE EXTENDED sap_bdc.hr.employee_records;

-- Then add column with proper data type
ALTER TABLE sap_bdc.hr.employee_records
ADD COLUMN performance_rating DECIMAL(3,2);

-- Example 14: Evolution with data validation
-- Add column and immediately validate existing data
ALTER TABLE sap_bdc.finance.transactions
ADD COLUMN transaction_category STRING;

-- Update new column based on existing patterns
UPDATE sap_bdc.finance.transactions
SET transaction_category = CASE
    WHEN account_type = 'EXPENSE' THEN 'Operating Expense'
    WHEN account_type = 'REVENUE' THEN 'Revenue'
    WHEN account_type = 'ASSET' THEN 'Asset Movement'
    ELSE 'Other'
END
WHERE transaction_category IS NULL;

-- Example 15: Schema evolution for SAP integration
-- Add columns to track SAP system metadata
ALTER TABLE sap_bdc.sales.orders
ADD COLUMNS (
    sap_source_system STRING COMMENT 'Source SAP system (S/4HANA, ECC, etc.)',
    sap_logical_system STRING COMMENT 'SAP logical system identifier',
    sap_last_modified_by STRING COMMENT 'SAP user who last modified the record',
    sap_last_modified_at TIMESTAMP COMMENT 'SAP modification timestamp'
);

-- Example 16: Create new table with evolved schema
-- Based on existing table but with additional fields
CREATE TABLE sap_bdc.hr.employee_records_v2
USING iceberg
AS SELECT
    employee_id,
    employee_name,
    department,
    hire_date,
    salary,
    -- Add computed columns
    YEAR(CURRENT_DATE) - YEAR(hire_date) AS years_of_service,
    -- Add placeholders for new data
    CAST(NULL AS BOOLEAN) AS remote_work_eligible,
    CAST(NULL AS STRING) AS office_location
FROM sap_bdc.hr.employee_records;

-- Example 17: Drop and recreate column (when type narrowing is needed)
-- Note: This is a metadata-only operation in Iceberg
ALTER TABLE sap_bdc.supply_chain.shipments
DROP COLUMN estimated_delivery_date;

ALTER TABLE sap_bdc.supply_chain.shipments
ADD COLUMN estimated_delivery_date DATE;

-- Example 18: Schema evolution with constraints
-- Add column with NOT NULL after backfilling
ALTER TABLE sap_bdc.sales.products
ADD COLUMN product_category STRING;

-- Backfill data first
UPDATE sap_bdc.sales.products
SET product_category = 'UNCATEGORIZED'
WHERE product_category IS NULL;

-- Now enforce constraint in application layer
-- (Iceberg supports schema but constraints are application-enforced)

-- Example 19: Evolution for partitioning columns
-- Add column that will be used for future partitioning
ALTER TABLE sap_bdc.sales.transactions
ADD COLUMN region STRING;

-- Update based on existing customer data
UPDATE sap_bdc.sales.transactions t
SET t.region = c.region
FROM sap_bdc.sales.customers c
WHERE t.customer_id = c.customer_id;

-- Example 20: View current table schema
-- Inspect all columns and their types
SELECT
    column_name,
    data_type,
    comment
FROM information_schema.columns
WHERE table_name = 'employee_records'
  AND table_schema = 'hr'
  AND table_catalog = 'sap_bdc'
ORDER BY ordinal_position;
