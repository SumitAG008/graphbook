# Databricks Integration Architecture

## Overview

This architecture demonstrates how to consume SAP Business Data Cloud (BDC) data products on Databricks using Apache Iceberg and Delta Sharing for zero-copy access.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         SAP Landscape                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ SAP S/4HANA  │  │ SuccessFactors│  │  SAP Integration    │  │
│  │              │  │               │  │      Suite          │  │
│  │  (ERP Data)  │  │   (HR Data)   │  │   (SAP Graph API)   │  │
│  └──────┬───────┘  └───────┬───────┘  └──────────┬───────────┘  │
│         │                  │                     │              │
│         └──────────────────┴─────────────────────┘              │
│                            │                                     │
└────────────────────────────┼─────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              SAP Business Data Cloud (BDC)                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Data Products (Curated)                     │   │
│  │  - General Ledger    - Employee Records                  │   │
│  │  - Sales Orders      - Customer Master                   │   │
│  │  - Delivery Data     - Product Catalog                   │   │
│  └────────────────────────┬─────────────────────────────────┘   │
│                           │                                     │
│  ┌────────────────────────┴─────────────────────────────────┐   │
│  │         Iceberg Tables (Open Table Format)              │   │
│  │  - Schema evolution    - Time travel                     │   │
│  │  - Snapshot isolation  - Hidden partitioning             │   │
│  └────────────────────────┬─────────────────────────────────┘   │
└────────────────────────────┼─────────────────────────────────────┘
                             │
                    ┌────────┴────────┐
                    │  Delta Sharing  │
                    │   Protocol      │
                    └────────┬────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Databricks Lakehouse                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                Unity Catalog                             │   │
│  │  - Shared Data Products  - Governance  - Lineage         │   │
│  └────────────────────────┬─────────────────────────────────┘   │
│                           │                                     │
│  ┌────────────────────────┴─────────────────────────────────┐   │
│  │              Compute Clusters                            │   │
│  │  - Spark SQL  - Python  - Scala  - R                     │   │
│  └────────────────────────┬─────────────────────────────────┘   │
│                           │                                     │
│  ┌────────────────────────┴─────────────────────────────────┐   │
│  │          Analytics & ML Workloads                        │   │
│  │  - Notebooks  - Jobs  - Workflows  - ML Models           │   │
│  └────────────────────────┬─────────────────────────────────┘   │
└────────────────────────────┼─────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │   Downstream   │
                    │ Consumers (BI, │
                    │   Apps, APIs)  │
                    └────────────────┘
```

## Components

### SAP Business Data Cloud (BDC)
- **Purpose**: Centralized data platform for SAP data products
- **Features**:
  - Semantic data modeling
  - Data federation across SAP sources
  - Zero-copy sharing via Delta Sharing
- **Integration**: Publishes Iceberg tables consumable by Databricks

### Delta Sharing
- **Purpose**: Open protocol for secure data sharing
- **Features**:
  - Zero-copy access (no data movement)
  - Fine-grained access control
  - Audit logging
- **Configuration**: Requires Delta Sharing profile URL and bearer token

### Databricks Lakehouse
- **Purpose**: Unified analytics platform
- **Features**:
  - Native Iceberg support
  - Unity Catalog for governance
  - Photon engine for performance
- **Integration**: Consumes BDC data products via Delta Sharing

## Implementation Steps

### Step 1: Configure Delta Sharing in SAP BDC

1. Enable Delta Sharing in BDC workspace
2. Create a share with data products:
   ```sql
   CREATE SHARE sap_bdc_finance
   ADD TABLE general_ledger
   ADD TABLE accounts_payable
   ADD TABLE accounts_receivable;
   ```
3. Generate Delta Sharing credentials
4. Configure recipient access

### Step 2: Connect Databricks to Delta Sharing

1. Create Delta Sharing credential in Databricks:
   ```python
   # Configure in Databricks workspace
   spark.conf.set("spark.databricks.delta.sharing.profile.url",
                  "https://bdc.sap/delta-sharing/profile")
   spark.conf.set("spark.databricks.delta.sharing.bearer.token",
                  "<bearer-token>")
   ```

2. Create external catalog in Unity Catalog:
   ```sql
   CREATE CATALOG sap_bdc
   USING DELTA_SHARING
   LOCATION '<delta-sharing-profile-url>';
   ```

### Step 3: Query SAP Data Products

1. Access shared tables:
   ```sql
   -- List available shares
   SHOW SCHEMAS IN sap_bdc;

   -- Query SAP data product
   SELECT * FROM sap_bdc.finance.general_ledger
   WHERE fiscal_year = 2025;
   ```

2. Use Iceberg time travel:
   ```sql
   -- Query historical data
   SELECT * FROM sap_bdc.finance.general_ledger
   FOR SYSTEM_TIME AS OF '2024-12-31 23:59:59';
   ```

### Step 4: Integrate SAP Graph API

1. Set up SAP BTP destination in Databricks secrets:
   ```python
   from pyspark.sql import SparkSession

   # Retrieve SAP Graph credentials
   graph_url = dbutils.secrets.get("sap", "graph-url")
   client_id = dbutils.secrets.get("sap", "client-id")
   client_secret = dbutils.secrets.get("sap", "client-secret")
   ```

2. Call SAP Graph API and enrich data:
   ```python
   import requests

   # Get OAuth token
   token_url = f"{graph_url}/oauth/token"
   token_response = requests.post(token_url, data={
       "grant_type": "client_credentials",
       "client_id": client_id,
       "client_secret": client_secret
   })
   access_token = token_response.json()["access_token"]

   # Query SAP Graph
   headers = {"Authorization": f"Bearer {access_token}"}
   response = requests.get(f"{graph_url}/v1/SalesOrders", headers=headers)

   # Convert to DataFrame
   graph_df = spark.read.json(sc.parallelize([response.text]))

   # Join with Iceberg data
   iceberg_df = spark.table("sap_bdc.sales.orders")
   enriched_df = iceberg_df.join(graph_df, "order_id")
   ```

### Step 5: Create Analytics Workflows

1. Build Delta tables from shared data:
   ```python
   # Create optimized analytics table
   (spark.table("sap_bdc.finance.general_ledger")
    .write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable("analytics.gl_analytics"))
   ```

2. Schedule data refresh jobs:
   ```python
   # Databricks job configuration
   {
     "name": "SAP_BDC_Refresh",
     "schedule": {
       "quartz_cron_expression": "0 0 2 * * ?",
       "timezone_id": "UTC"
     },
     "tasks": [
       {
         "task_key": "refresh_analytics",
         "notebook_task": {
           "notebook_path": "/Shared/SAP_BDC/refresh_pipeline"
         }
       }
     ]
   }
   ```

## Best Practices

### Performance Optimization

1. **Use Photon Engine**
   - Enable on compute clusters for 3-5x performance
   - Optimal for scanning Iceberg tables

2. **Partition Pruning**
   - Leverage Iceberg's hidden partitioning
   - Filter on partition columns (date, region, etc.)

3. **File Compaction**
   ```sql
   -- Optimize file layout
   OPTIMIZE sap_bdc.sales.orders
   WHERE order_date >= '2025-01-01';
   ```

4. **Z-Ordering**
   ```sql
   -- Improve filter performance
   OPTIMIZE sap_bdc.sales.orders
   ZORDER BY (customer_id, order_date);
   ```

### Security & Governance

1. **Unity Catalog Integration**
   - Register shared data products in Unity Catalog
   - Apply row-level and column-level security
   - Track lineage automatically

2. **Credential Management**
   - Store SAP credentials in Databricks secrets
   - Use service principals for automation
   - Rotate credentials regularly

3. **Access Control**
   ```sql
   -- Grant access to shared data
   GRANT SELECT ON CATALOG sap_bdc TO `data-analysts`;
   GRANT SELECT ON SCHEMA sap_bdc.finance TO `finance-team`;
   ```

### Cost Optimization

1. **Auto-scaling Clusters**
   - Use serverless SQL warehouses for ad-hoc queries
   - Configure auto-scaling for job clusters

2. **Delta Sharing Benefits**
   - Zero storage costs (no data copy)
   - Pay only for compute when querying
   - Automatic updates from SAP BDC

3. **Intelligent Caching**
   - Enable Databricks I/O cache
   - Cache frequently accessed data products

## Monitoring & Troubleshooting

### Query Performance

```sql
-- Analyze query execution
EXPLAIN EXTENDED
SELECT * FROM sap_bdc.finance.general_ledger
WHERE fiscal_year = 2025;

-- View table statistics
DESCRIBE EXTENDED sap_bdc.finance.general_ledger;
```

### Delta Sharing Status

```python
# Check Delta Sharing connection
shares = spark.sql("SHOW SHARES").collect()
for share in shares:
    print(f"Share: {share.name}, Provider: {share.provider}")
```

### Lineage Tracking

```sql
-- View data lineage in Unity Catalog
SELECT *
FROM system.access.table_lineage
WHERE target_table_full_name = 'analytics.gl_analytics';
```

## Example Use Cases

### Finance Reconciliation

```sql
-- Compare month-end balances
WITH current_balance AS (
    SELECT account_number, SUM(amount) AS balance
    FROM sap_bdc.finance.general_ledger
    WHERE posting_date <= LAST_DAY(CURRENT_DATE)
    GROUP BY account_number
),
previous_balance AS (
    SELECT account_number, SUM(amount) AS balance
    FROM sap_bdc.finance.general_ledger
    FOR SYSTEM_TIME AS OF LAST_DAY(ADD_MONTHS(CURRENT_DATE, -1))
    GROUP BY account_number
)
SELECT
    c.account_number,
    p.balance AS prev_month_balance,
    c.balance AS current_balance,
    c.balance - p.balance AS variance
FROM current_balance c
LEFT JOIN previous_balance p ON c.account_number = p.account_number
WHERE ABS(c.balance - COALESCE(p.balance, 0)) > 1000;
```

### Customer 360 Analytics

```python
# Combine SAP data with Graph API
from pyspark.sql.functions import col, sum, avg, count

# SAP BDC data products
customers_df = spark.table("sap_bdc.sales.customers")
orders_df = spark.table("sap_bdc.sales.orders")

# Customer analytics
customer_360 = (orders_df
    .groupBy("customer_id")
    .agg(
        count("order_id").alias("total_orders"),
        sum("order_amount").alias("lifetime_value"),
        avg("order_amount").alias("avg_order_value"),
        max("order_date").alias("last_order_date")
    )
    .join(customers_df, "customer_id")
    .select(
        "customer_id",
        "customer_name",
        "customer_segment",
        "total_orders",
        "lifetime_value",
        "avg_order_value",
        "last_order_date"
    ))

customer_360.write.format("delta").saveAsTable("analytics.customer_360")
```

## Resources

- [Databricks Delta Sharing Guide](https://docs.databricks.com/data-sharing/index.html)
- [Unity Catalog Documentation](https://docs.databricks.com/data-governance/unity-catalog/index.html)
- [Apache Iceberg on Databricks](https://docs.databricks.com/delta/uniform.html)
- [SAP BDC Integration](https://help.sap.com/docs/sap-datasphere)
