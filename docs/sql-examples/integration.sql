-- ========================================================
-- Iceberg + SAP Graph + BDC Integration Examples
-- ========================================================

-- Example 1: Join SAP Graph data with Iceberg tables
-- Enrich order data with real-time customer information from SAP Graph
WITH graph_customers AS (
    -- Assume this CTE represents data fetched from SAP Graph API
    -- In practice, use Spark connector or staged data
    SELECT
        customer_id,
        customer_name,
        customer_segment,
        credit_limit
    FROM sap_graph.business_partners
),
iceberg_orders AS (
    SELECT
        order_id,
        customer_id,
        order_date,
        order_amount,
        status
    FROM sap_bdc.sales.orders
    WHERE order_date >= CURRENT_DATE - INTERVAL 30 DAYS
)
SELECT
    o.order_id,
    o.order_date,
    c.customer_name,
    c.customer_segment,
    o.order_amount,
    c.credit_limit,
    CASE
        WHEN o.order_amount > c.credit_limit * 0.8
        THEN 'Credit Review Required'
        ELSE 'OK'
    END AS credit_check_status
FROM iceberg_orders o
LEFT JOIN graph_customers c ON o.customer_id = c.customer_id;

-- Example 2: Time travel with SAP Graph reconciliation
-- Compare historical Iceberg data with current SAP Graph state
WITH historical_employees AS (
    SELECT
        employee_id,
        employee_name,
        department,
        salary
    FROM sap_bdc.hr.employee_records
    FOR SYSTEM_TIME AS OF '2024-12-31 23:59:59'
),
current_sap_employees AS (
    SELECT
        employee_id,
        employee_name,
        department,
        salary
    FROM sap_graph.employees
)
SELECT
    h.employee_id,
    h.employee_name,
    h.department AS prev_department,
    c.department AS current_department,
    h.salary AS prev_salary,
    c.salary AS current_salary,
    c.salary - h.salary AS salary_change
FROM historical_employees h
INNER JOIN current_sap_employees c ON h.employee_id = c.employee_id
WHERE h.department != c.department OR h.salary != c.salary;

-- Example 3: IoT + SAP Deliveries integration
-- Correlate sensor data from Iceberg with delivery schedules from SAP Graph
SELECT
    d.delivery_id,
    d.delivery_date,
    d.destination,
    d.status AS delivery_status,
    COUNT(s.sensor_id) AS sensor_reading_count,
    AVG(s.temperature) AS avg_temperature,
    MAX(s.temperature) AS max_temperature,
    MIN(s.temperature) AS min_temperature
FROM sap_graph.deliveries d
INNER JOIN sap_bdc.iot.shipment_sensors s
    ON d.delivery_id = s.delivery_id
    AND s.reading_timestamp BETWEEN d.start_time AND d.end_time
WHERE d.delivery_date >= CURRENT_DATE - INTERVAL 7 DAYS
GROUP BY d.delivery_id, d.delivery_date, d.destination, d.status
HAVING AVG(s.temperature) > 25.0; -- Flag temperature-sensitive shipments

-- Example 4: Finance reconciliation with time travel
-- Audit trail combining Iceberg snapshots and SAP Graph ledger
WITH iceberg_snapshot AS (
    SELECT
        account_number,
        SUM(amount) AS snapshot_balance
    FROM sap_bdc.finance.general_ledger
    FOR SYSTEM_TIME AS OF '2024-12-31 23:59:59'
    GROUP BY account_number
),
sap_current AS (
    SELECT
        account_number,
        balance AS current_balance
    FROM sap_graph.gl_accounts
)
SELECT
    i.account_number,
    i.snapshot_balance AS year_end_balance,
    s.current_balance,
    s.current_balance - i.snapshot_balance AS ytd_change,
    CASE
        WHEN ABS(s.current_balance - i.snapshot_balance) > 1000
        THEN 'Material Variance'
        ELSE 'OK'
    END AS variance_flag
FROM iceberg_snapshot i
FULL OUTER JOIN sap_current s ON i.account_number = s.account_number;

-- Example 5: Supply chain visibility with Graph traversal
-- Navigate SAP Graph relationships and enrich with Iceberg analytics
WITH order_network AS (
    -- SAP Graph: traverse Orders -> OrderItems -> Products
    SELECT
        o.order_id,
        o.customer_id,
        oi.product_id,
        oi.quantity,
        p.product_name,
        p.supplier_id
    FROM sap_graph.orders o
    INNER JOIN sap_graph.order_items oi ON o.order_id = oi.order_id
    INNER JOIN sap_graph.products p ON oi.product_id = p.product_id
    WHERE o.order_date >= CURRENT_DATE - INTERVAL 90 DAYS
),
inventory_analytics AS (
    SELECT
        product_id,
        AVG(stock_level) AS avg_stock,
        MIN(stock_level) AS min_stock,
        MAX(stock_level) AS max_stock
    FROM sap_bdc.supply_chain.inventory
    WHERE snapshot_date >= CURRENT_DATE - INTERVAL 90 DAYS
    GROUP BY product_id
)
SELECT
    on.order_id,
    on.product_name,
    on.quantity,
    ia.avg_stock,
    ia.min_stock,
    CASE
        WHEN ia.min_stock < on.quantity THEN 'Stock Risk'
        ELSE 'Sufficient Stock'
    END AS stock_status
FROM order_network on
LEFT JOIN inventory_analytics ia ON on.product_id = ia.product_id;

-- Example 6: Zero-copy data sharing to Databricks
-- Query SAP BDC data products directly in Databricks via Delta Sharing
-- Configuration in Databricks:
-- USING deltaSharing
-- LOCATION '<delta-sharing-profile-url>'

-- Query shared SAP data product
SELECT
    company_code,
    fiscal_year,
    fiscal_period,
    SUM(debit_amount) AS total_debits,
    SUM(credit_amount) AS total_credits,
    SUM(debit_amount) - SUM(credit_amount) AS net_amount
FROM delta.`#share_name.schema_name.general_ledger`
WHERE fiscal_year = 2025
GROUP BY company_code, fiscal_year, fiscal_period;

-- Example 7: Microsoft Fabric integration with SAP BDC
-- Use OneLake shortcuts to access SAP data products
-- Query through Fabric Lakehouse
SELECT
    employee_id,
    employee_name,
    department,
    hire_date,
    DATEDIFF(CURRENT_DATE, hire_date) AS days_employed
FROM lakehouse_sap_data_products.hr.employees
WHERE status = 'Active';

-- Example 8: Combine Microsoft Graph with SAP data
-- Enrich SAP employee data with Microsoft 365 activity
WITH m365_activity AS (
    SELECT
        user_principal_name,
        last_activity_date,
        email_count,
        meeting_count,
        teams_chat_count
    FROM microsoft_graph.user_activity
),
sap_employees AS (
    SELECT
        employee_id,
        email AS user_principal_name,
        department,
        manager_id
    FROM sap_bdc.hr.employee_records
)
SELECT
    e.employee_id,
    e.department,
    m.last_activity_date,
    m.email_count,
    m.meeting_count,
    m.teams_chat_count,
    CASE
        WHEN m.last_activity_date < CURRENT_DATE - INTERVAL 7 DAYS
        THEN 'Inactive'
        ELSE 'Active'
    END AS activity_status
FROM sap_employees e
LEFT JOIN m365_activity m ON e.user_principal_name = m.user_principal_name;

-- Example 9: Real-time SAP Graph + batch Iceberg analytics
-- Combine streaming SAP events with historical analysis
WITH real_time_orders AS (
    -- SAP Graph: real-time order events
    SELECT
        order_id,
        customer_id,
        order_amount,
        CURRENT_TIMESTAMP AS query_time
    FROM sap_graph.orders
    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL 1 HOUR
),
customer_history AS (
    -- Iceberg: historical customer behavior
    SELECT
        customer_id,
        COUNT(DISTINCT order_id) AS lifetime_orders,
        SUM(order_amount) AS lifetime_value,
        AVG(order_amount) AS avg_order_value
    FROM sap_bdc.sales.orders
    GROUP BY customer_id
)
SELECT
    r.order_id,
    r.customer_id,
    r.order_amount,
    h.lifetime_orders,
    h.lifetime_value,
    h.avg_order_value,
    CASE
        WHEN r.order_amount > h.avg_order_value * 2
        THEN 'High Value Order'
        WHEN h.lifetime_orders = 0
        THEN 'New Customer'
        ELSE 'Regular Order'
    END AS order_classification
FROM real_time_orders r
LEFT JOIN customer_history h ON r.customer_id = h.customer_id;

-- Example 10: SAP S/4HANA CDS Views via Graph + Iceberg persistence
-- Extract SAP CDS view data and persist to Iceberg for analytics
-- Stage 1: Extract from SAP Graph (representing CDS view)
CREATE OR REPLACE TABLE sap_bdc.finance.cds_revenue_snapshot
USING iceberg
AS
SELECT
    sales_document,
    sales_document_item,
    material,
    customer,
    net_value,
    currency,
    billing_date,
    company_code,
    CURRENT_TIMESTAMP AS snapshot_time
FROM sap_graph.cds_views.i_billing_document_item
WHERE billing_date >= '2025-01-01';

-- Stage 2: Query with time travel for auditing
SELECT
    company_code,
    material,
    SUM(net_value) AS total_revenue
FROM sap_bdc.finance.cds_revenue_snapshot
FOR SYSTEM_TIME AS OF '2025-01-31 23:59:59'
GROUP BY company_code, material;

-- Example 11: Cross-system data lineage
-- Track data movement from SAP -> Iceberg -> Analytics
WITH sap_source AS (
    SELECT
        order_id,
        'SAP_S4HANA' AS source_system,
        last_changed_at AS source_timestamp
    FROM sap_graph.orders
),
iceberg_staging AS (
    SELECT
        order_id,
        'ICEBERG_LAKE' AS target_system,
        _iceberg_commit_time AS ingestion_time
    FROM sap_bdc.sales.orders.snapshots s
    CROSS JOIN sap_bdc.sales.orders o
    WHERE s.snapshot_id = o._iceberg_snapshot_id
)
SELECT
    src.order_id,
    src.source_system,
    src.source_timestamp,
    stg.target_system,
    stg.ingestion_time,
    TIMESTAMPDIFF(MINUTE, src.source_timestamp, stg.ingestion_time) AS latency_minutes
FROM sap_source src
LEFT JOIN iceberg_staging stg ON src.order_id = stg.order_id;

-- Example 12: Multi-cloud data product consumption
-- Query SAP BDC data products from both Databricks and Fabric
-- Databricks query (Delta Sharing)
-- SELECT * FROM delta_sharing.sap_bdc.sales.orders;

-- Fabric query (OneLake shortcut)
-- SELECT * FROM lakehouse.sap_bdc.sales.orders;

-- Example 13: SAP Graph mutation + Iceberg audit trail
-- Track changes made via SAP Graph API in Iceberg for compliance
CREATE TABLE sap_bdc.audit.graph_api_changes (
    change_id STRING,
    entity_type STRING,
    entity_id STRING,
    operation STRING,
    changed_by STRING,
    changed_at TIMESTAMP,
    old_values MAP<STRING, STRING>,
    new_values MAP<STRING, STRING>
)
USING iceberg
PARTITIONED BY (days(changed_at));

-- Insert audit records after SAP Graph mutations
INSERT INTO sap_bdc.audit.graph_api_changes
VALUES (
    'CHG-12345',
    'Customer',
    'CUST-67890',
    'UPDATE',
    'john.doe@example.com',
    CURRENT_TIMESTAMP,
    map('credit_limit', '50000', 'payment_terms', 'Net30'),
    map('credit_limit', '75000', 'payment_terms', 'Net45')
);

-- Example 14: Iceberg materialized views with SAP Graph refresh
-- Pre-aggregate data for fast queries, refresh from SAP Graph periodically
CREATE OR REPLACE TABLE sap_bdc.analytics.customer_360_view
USING iceberg
AS
SELECT
    c.customer_id,
    c.customer_name,
    c.customer_segment,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(o.order_amount) AS total_revenue,
    MAX(o.order_date) AS last_order_date,
    AVG(o.order_amount) AS avg_order_value
FROM sap_graph.customers c
LEFT JOIN sap_bdc.sales.orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name, c.customer_segment;

-- Refresh periodically (scheduled job)
-- REFRESH TABLE sap_bdc.analytics.customer_360_view;

-- Example 15: Complex Graph traversal + Iceberg aggregation
-- Navigate SAP Graph: Customer -> Orders -> Deliveries
-- Combine with Iceberg delivery performance analytics
WITH customer_deliveries AS (
    SELECT
        c.customer_id,
        c.customer_name,
        o.order_id,
        d.delivery_id,
        d.planned_delivery_date,
        d.actual_delivery_date
    FROM sap_graph.customers c
    INNER JOIN sap_graph.orders o ON c.customer_id = o.customer_id
    INNER JOIN sap_graph.deliveries d ON o.order_id = d.order_id
    WHERE o.order_date >= '2025-01-01'
),
delivery_metrics AS (
    SELECT
        delivery_id,
        AVG(on_time_score) AS avg_on_time_score
    FROM sap_bdc.supply_chain.delivery_performance
    GROUP BY delivery_id
)
SELECT
    cd.customer_id,
    cd.customer_name,
    COUNT(DISTINCT cd.delivery_id) AS total_deliveries,
    AVG(DATEDIFF(cd.actual_delivery_date, cd.planned_delivery_date)) AS avg_delay_days,
    AVG(dm.avg_on_time_score) AS avg_on_time_score,
    CASE
        WHEN AVG(dm.avg_on_time_score) >= 0.95 THEN 'Excellent'
        WHEN AVG(dm.avg_on_time_score) >= 0.85 THEN 'Good'
        ELSE 'Needs Improvement'
    END AS delivery_rating
FROM customer_deliveries cd
LEFT JOIN delivery_metrics dm ON cd.delivery_id = dm.delivery_id
GROUP BY cd.customer_id, cd.customer_name;
