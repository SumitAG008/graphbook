# Apache Iceberg: Free, Open-Source & Real-World Business Cases

## Table of Contents
1. [Is Apache Iceberg Free?](#is-apache-iceberg-free)
2. [Real Companies Using Apache Iceberg](#real-companies-using-apache-iceberg)
3. [Modern Business Cases (2025)](#modern-business-cases-2025)
4. [Implementation Guide](#implementation-guide)
5. [Cost Analysis & ROI](#cost-analysis--roi)
6. [When to Use vs When NOT to Use](#when-to-use-vs-when-not-to-use)

---

## 1. Is Apache Iceberg Free?

### ✅ YES - Completely Free & Open Source

**License**: Apache License 2.0
- **Free to use**: For commercial and non-commercial purposes
- **No licensing fees**: Ever
- **No vendor lock-in**: Open standard, multiple vendors support it
- **Community-driven**: Apache Software Foundation project
- **Source code**: Publicly available on GitHub

### What's Free:
- ✅ The Iceberg table format specification
- ✅ Libraries and SDKs (Java, Python, Rust)
- ✅ All features (time travel, schema evolution, ACID transactions)
- ✅ Integration with all engines (Spark, Flink, Trino, Dremio, etc.)
- ✅ Community support and documentation

### What You Pay For:
- ❌ **Storage costs**: S3, HDFS, Azure Data Lake (normal cloud storage pricing)
- ❌ **Compute costs**: Spark/Flink clusters to process data
- ❌ **Managed services** (optional): Databricks, AWS Glue, Snowflake, Dremio
- ❌ **Support contracts** (optional): Commercial support from vendors

### Comparison with Alternatives

| Feature | Apache Iceberg | Delta Lake | Apache Hudi |
|---------|---------------|------------|-------------|
| **License** | Apache 2.0 (Free) | Apache 2.0 (Free) | Apache 2.0 (Free) |
| **Vendor** | Apache Foundation | Databricks (Linux Foundation) | Apache Foundation |
| **Open Standard** | ✅ Yes | ⚠️ Partial | ✅ Yes |
| **Multi-engine** | ✅ All engines | ⚠️ Limited | ⚠️ Limited |
| **Hidden Partitioning** | ✅ Yes | ❌ No | ❌ No |
| **Time Travel** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Schema Evolution** | ✅ Full support | ⚠️ Limited | ⚠️ Limited |

**Winner**: Iceberg has the most vendor-neutral, engine-agnostic approach.

---

## 2. Real Companies Using Apache Iceberg

### 🏢 Fortune 500 & Tech Giants

#### **Netflix** (Pioneer)
- **Use Case**: Petabyte-scale data lake
- **Volume**: 100+ PB of data
- **Benefits**:
  - Replaced Hive tables with Iceberg
  - 10x faster query performance
  - Saved millions in storage costs
- **Quote**: "Iceberg solved our metadata scalability issues"

#### **Apple**
- **Use Case**: User analytics and ML pipelines
- **Scale**: Multiple petabytes
- **Benefits**:
  - Real-time data ingestion
  - ACID guarantees for critical data
  - Simplified data governance

#### **Adobe**
- **Use Case**: Customer experience analytics
- **Implementation**: Adobe Experience Platform Data Lake
- **Benefits**:
  - Multi-tenant data isolation
  - Fast analytics on customer behavior
  - Reduced operational complexity

#### **Airbnb**
- **Use Case**: Search and recommendation systems
- **Scale**: Billions of events daily
- **Benefits**:
  - Faster feature engineering for ML
  - Improved data freshness
  - Better resource utilization

#### **LinkedIn**
- **Use Case**: Member analytics and insights
- **Implementation**: Unified analytics platform
- **Benefits**:
  - Consistent data across teams
  - Reduced data duplication
  - Faster time-to-insight

#### **Expedia Group**
- **Use Case**: Travel data analytics
- **Scale**: Petabyte-scale customer and booking data
- **Benefits**:
  - Improved data reliability
  - Faster query performance
  - Cost optimization

#### **Salesforce**
- **Use Case**: Customer data platform
- **Benefits**:
  - Multi-tenant data management
  - GDPR compliance with time travel
  - Real-time analytics

### 🚀 Unicorn Startups

#### **Tabular** (Founded by Iceberg creators)
- Founded by Ryan Blue, Daniel Weeks, Jason Reid (Iceberg creators)
- Provides managed Iceberg services
- Customers: Major enterprises migrating to Iceberg

#### **Dremio**
- **Product**: Lakehouse platform built on Iceberg
- **Use Case**: SQL analytics on data lakes
- **Customers**: 100+ enterprises

### 🏦 Financial Services

#### **Goldman Sachs**
- **Use Case**: Risk analytics and compliance
- **Benefits**: Audit trail with time travel, ACID transactions

#### **JPMorgan Chase**
- **Use Case**: Fraud detection and transaction analysis
- **Benefits**: Real-time analytics, historical analysis

### 🏥 Healthcare

#### **Major Healthcare Provider** (Anonymous)
- **Use Case**: Patient data analytics
- **Benefits**: HIPAA compliance, data versioning, audit trails

---

## 3. Modern Business Cases (2025)

### Business Case #1: **Real-Time Customer Data Platform (CDP)**

#### Problem Statement
Modern businesses collect customer data from 10+ sources:
- Website clicks (millions/day)
- Mobile app events
- CRM systems (Salesforce, SAP)
- Customer service interactions
- Purchase transactions
- Social media engagement

**Challenges**:
- Data arrives continuously
- Need real-time + historical analysis
- GDPR compliance (right to be forgotten)
- Multiple teams need different views of data

#### Iceberg Solution

```
┌─────────────────────────────────────────────────┐
│         Data Sources (Real-time)                │
│  Web, Mobile, CRM, Support, Transactions        │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│         Streaming Ingestion (Kafka)             │
│  Topics: clicks, purchases, support, etc.       │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│      Stream Processing (Flink/Spark)            │
│  - Data validation & enrichment                 │
│  - PII detection & masking                      │
│  - Real-time aggregations                       │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│         Apache Iceberg Tables                   │
│                                                 │
│  customer_events/                               │
│  ├── year=2025/                                 │
│  │   ├── month=01/                              │
│  │   │   └── day=15/                            │
│  │   │       └── data-001.parquet               │
│                                                 │
│  Features:                                      │
│  - ACID writes (no duplicates)                  │
│  - Schema evolution (add new fields)            │
│  - Time travel (GDPR compliance)                │
│  - Partitioning (fast queries)                  │
└─────────────────────────────────────────────────┘
                    ↓
        ┌───────────┴───────────┐
        ↓                       ↓
┌──────────────────┐    ┌──────────────────┐
│  Real-time       │    │  Historical      │
│  Analytics       │    │  Analytics       │
│  (Trino/Presto)  │    │  (Spark/Dremio)  │
└──────────────────┘    └──────────────────┘
```

#### Implementation Example

```python
# Write streaming data to Iceberg
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("CDP-Iceberg") \
    .config("spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config("spark.sql.catalog.lakehouse",
            "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.lakehouse.type", "hadoop") \
    .config("spark.sql.catalog.lakehouse.warehouse", "s3://my-data-lake") \
    .getOrCreate()

# Create Iceberg table
spark.sql("""
    CREATE TABLE IF NOT EXISTS lakehouse.customer_events (
        customer_id STRING,
        event_type STRING,
        event_timestamp TIMESTAMP,
        event_properties MAP<STRING, STRING>,
        source_system STRING,
        ingestion_timestamp TIMESTAMP
    )
    USING iceberg
    PARTITIONED BY (days(event_timestamp))
    TBLPROPERTIES (
        'write.format.default' = 'parquet',
        'write.metadata.compression-codec' = 'gzip'
    )
""")

# Stream from Kafka to Iceberg
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "customer-events") \
    .load()

# Write to Iceberg with exactly-once semantics
query = kafka_df.selectExpr(
    "CAST(value AS STRING) as json_data"
).selectExpr(
    "from_json(json_data, 'customer_id STRING, event_type STRING...') as data"
).select("data.*") \
.writeStream \
    .format("iceberg") \
    .outputMode("append") \
    .trigger(processingTime="10 seconds") \
    .option("checkpointLocation", "s3://checkpoints/customer-events") \
    .toTable("lakehouse.customer_events")
```

#### GDPR Compliance with Time Travel

```sql
-- Delete customer data (GDPR right to be forgotten)
DELETE FROM lakehouse.customer_events
WHERE customer_id = 'user-123';

-- Audit: Verify what data existed before deletion
SELECT * FROM lakehouse.customer_events
TIMESTAMP AS OF '2025-01-15 10:00:00'
WHERE customer_id = 'user-123';

-- Regulatory reporting: Historical state
SELECT * FROM lakehouse.customer_events
VERSION AS OF 12345678  -- Snapshot ID
WHERE event_date = '2024-12-31';
```

#### Business Impact
- **Data Freshness**: < 10 seconds (vs. 24 hours with batch)
- **Storage Cost**: 40% reduction (Parquet compression + partitioning)
- **Query Performance**: 10x faster (metadata pruning)
- **Compliance**: Audit-ready with complete history
- **ROI**: $2M savings annually for mid-size company

---

### Business Case #2: **Financial Services - Trade Analytics**

#### Problem Statement
Investment banks process billions of trades daily:
- Market data (tick-by-tick prices)
- Trade executions
- Risk calculations
- Regulatory reporting (MiFID II, Dodd-Frank)

**Requirements**:
- Sub-second latency for risk calculations
- Immutable audit trail (regulatory)
- Historical analysis (backtesting strategies)
- Concurrent read/write without conflicts

#### Iceberg Solution Architecture

```sql
-- Create trade analytics table
CREATE TABLE lakehouse.trades (
    trade_id BIGINT,
    trader_id STRING,
    instrument STRING,
    quantity DECIMAL(18,2),
    price DECIMAL(18,6),
    trade_timestamp TIMESTAMP,
    settlement_date DATE,
    counterparty STRING,
    book STRING,
    regulatory_flags MAP<STRING, STRING>
)
USING iceberg
PARTITIONED BY (days(trade_timestamp), book)
TBLPROPERTIES (
    'write.metadata.metrics.default' = 'full',
    'commit.retry.num-retries' = '10'
)
```

#### Real-Time Risk Analytics

```python
# Calculate real-time Value-at-Risk (VaR)
from pyspark.sql import functions as F

# Read latest trades
trades_df = spark.table("lakehouse.trades") \
    .filter(F.col("trade_timestamp") > F.expr("current_timestamp() - INTERVAL 1 HOUR"))

# Join with market data
risk_df = trades_df \
    .join(market_data, "instrument") \
    .groupBy("book", "trader_id") \
    .agg(
        F.sum(F.col("quantity") * F.col("price")).alias("exposure"),
        F.sum(F.col("quantity") * F.col("price") * F.col("volatility")).alias("var_95")
    )

# Write risk metrics to Iceberg
risk_df.write \
    .format("iceberg") \
    .mode("overwrite") \
    .option("overwrite-mode", "dynamic") \
    .save("lakehouse.risk_metrics")
```

#### Regulatory Reporting with Time Travel

```sql
-- MiFID II: Report all trades as of market close
SELECT
    trade_id,
    trader_id,
    instrument,
    quantity,
    price,
    trade_timestamp
FROM lakehouse.trades
TIMESTAMP AS OF '2025-01-15 16:00:00'  -- Market close
WHERE regulatory_flags['mifid_reportable'] = 'true';

-- Audit: Investigate discrepancy
SELECT * FROM lakehouse.trades.history
WHERE trade_id = 'TRD-123456'
ORDER BY made_current_at DESC;
```

#### Benefits for Financial Services
- **Compliance**: Complete audit trail without custom logging
- **Performance**: 100x faster than traditional databases for analytics
- **Cost**: 60% reduction in storage (vs. Oracle/Teradata)
- **Risk Management**: Real-time risk calculations
- **Flexibility**: Schema evolution without downtime

---

### Business Case #3: **E-Commerce - Product Catalog & Recommendations**

#### Problem Statement
Modern e-commerce platforms have:
- Millions of SKUs with frequent updates
- Real-time inventory changes
- User behavior data (billions of events)
- Need for personalized recommendations

**Challenges**:
- Schema changes (new product attributes)
- High write concurrency (inventory updates)
- Fast reads for recommendations
- Historical analysis for trend detection

#### Iceberg Schema Evolution

```sql
-- Initial schema
CREATE TABLE lakehouse.product_catalog (
    product_id STRING,
    name STRING,
    category STRING,
    price DECIMAL(10,2),
    inventory_count INT,
    last_updated TIMESTAMP
)
USING iceberg;

-- Later: Add new attributes without rewriting data
ALTER TABLE lakehouse.product_catalog
ADD COLUMNS (
    sustainability_score FLOAT,
    carbon_footprint DECIMAL(10,2),
    supplier_diversity_flag BOOLEAN
);

-- Even later: Change partition strategy
ALTER TABLE lakehouse.product_catalog
SET PARTITION SPEC (category, bucket(16, product_id));
```

#### Real-Time Inventory Management

```python
# Streaming inventory updates
inventory_stream = spark.readStream \
    .format("kafka") \
    .option("subscribe", "inventory-updates") \
    .load()

# Merge updates into Iceberg (upsert pattern)
def upsert_inventory(batch_df, batch_id):
    batch_df.createOrReplaceTempView("updates")

    spark.sql("""
        MERGE INTO lakehouse.product_catalog AS target
        USING updates AS source
        ON target.product_id = source.product_id
        WHEN MATCHED THEN
            UPDATE SET
                target.inventory_count = source.inventory_count,
                target.last_updated = source.timestamp
        WHEN NOT MATCHED THEN
            INSERT *
    """)

inventory_stream.writeStream \
    .foreachBatch(upsert_inventory) \
    .start()
```

#### Recommendation Engine with Historical Data

```sql
-- Analyze purchase patterns over time
WITH customer_history AS (
    SELECT
        customer_id,
        product_id,
        purchase_timestamp,
        quantity
    FROM lakehouse.purchases
    WHERE purchase_timestamp >= current_date - INTERVAL '90 days'
),
product_affinity AS (
    SELECT
        p1.product_id as product_a,
        p2.product_id as product_b,
        COUNT(*) as co_purchase_count
    FROM customer_history p1
    JOIN customer_history p2
        ON p1.customer_id = p2.customer_id
        AND p1.product_id < p2.product_id
    GROUP BY p1.product_id, p2.product_id
    HAVING COUNT(*) > 10
)
SELECT * FROM product_affinity
ORDER BY co_purchase_count DESC;
```

#### Business Impact
- **Revenue**: 15% increase from better recommendations
- **Inventory Optimization**: 25% reduction in stockouts
- **Agility**: Add new product attributes in minutes (vs. days)
- **Cost**: 50% storage savings vs. traditional RDBMS

---

### Business Case #4: **Healthcare - Patient Journey Analytics**

#### Problem Statement
Healthcare providers need to:
- Track patient interactions across systems (EMR, lab, pharmacy, billing)
- Analyze treatment effectiveness
- Ensure HIPAA compliance
- Research long-term health outcomes

#### Iceberg for HIPAA Compliance

```sql
-- Patient events table
CREATE TABLE lakehouse.patient_events (
    patient_id_hash STRING,  -- PHI protected
    event_type STRING,
    event_timestamp TIMESTAMP,
    department STRING,
    diagnosis_codes ARRAY<STRING>,
    procedure_codes ARRAY<STRING>,
    provider_id STRING,
    encryption_key_version INT
)
USING iceberg
PARTITIONED BY (months(event_timestamp), department)
TBLPROPERTIES (
    'write.object-storage.enabled' = 'true',
    'write.encryption.enabled' = 'true'
);

-- Audit trail query
SELECT
    snapshot_id,
    made_current_at,
    operation,
    summary
FROM lakehouse.patient_events.snapshots
WHERE made_current_at >= current_date - INTERVAL '30 days';
```

#### Longitudinal Analysis

```sql
-- Analyze diabetes patient outcomes over 5 years
SELECT
    YEAR(event_timestamp) as year,
    AVG(CAST(lab_values['hba1c'] AS FLOAT)) as avg_hba1c,
    COUNT(DISTINCT patient_id_hash) as patient_count
FROM lakehouse.patient_events
WHERE array_contains(diagnosis_codes, 'E11')  -- Type 2 Diabetes
    AND event_timestamp >= current_date - INTERVAL '5 years'
GROUP BY YEAR(event_timestamp)
ORDER BY year;
```

#### Benefits
- **Compliance**: Complete audit trail for HIPAA
- **Research**: 5+ years of historical data instantly queryable
- **Privacy**: Data versioning supports patient data deletion
- **Cost**: 70% cheaper than proprietary healthcare data warehouses

---

### Business Case #5: **IoT & Manufacturing - Sensor Data Analytics**

#### Problem Statement
Smart factories generate:
- Sensor data (temperature, pressure, vibration)
- Equipment telemetry (100K+ devices)
- Quality control measurements
- Predictive maintenance requirements

**Scale**: Billions of sensor readings per day

#### Iceberg for Time-Series IoT Data

```sql
-- Sensor readings table
CREATE TABLE lakehouse.sensor_readings (
    device_id STRING,
    sensor_type STRING,
    reading_value DOUBLE,
    reading_timestamp TIMESTAMP,
    factory_location STRING,
    quality_flag STRING,
    metadata MAP<STRING, STRING>
)
USING iceberg
PARTITIONED BY (factory_location, hours(reading_timestamp))
TBLPROPERTIES (
    'write.distribution-mode' = 'hash',  -- Better write performance
    'write.parquet.row-group-size-bytes' = '134217728'  -- 128MB
);
```

#### Predictive Maintenance

```python
# Detect anomalies in sensor data
from pyspark.sql.window import Window

sensor_df = spark.table("lakehouse.sensor_readings") \
    .filter(F.col("reading_timestamp") > F.expr("current_timestamp() - INTERVAL 7 DAYS"))

# Calculate rolling statistics
window_spec = Window.partitionBy("device_id", "sensor_type") \
    .orderBy("reading_timestamp") \
    .rowsBetween(-100, 0)

anomalies_df = sensor_df.withColumn(
    "rolling_avg", F.avg("reading_value").over(window_spec)
).withColumn(
    "rolling_std", F.stddev("reading_value").over(window_spec)
).withColumn(
    "z_score",
    (F.col("reading_value") - F.col("rolling_avg")) / F.col("rolling_std")
).filter(
    F.abs(F.col("z_score")) > 3  -- 3-sigma rule
)

# Alert on anomalies
anomalies_df.write \
    .format("iceberg") \
    .mode("append") \
    .save("lakehouse.maintenance_alerts")
```

#### Benefits
- **Downtime Reduction**: 40% fewer unplanned outages
- **Cost Savings**: $5M annually in avoided downtime
- **Efficiency**: Real-time alerts vs. weekly reports
- **Scalability**: Handles 10x data growth without architecture changes

---

### Business Case #6: **Media & Entertainment - Content Analytics**

#### Problem Statement
Streaming platforms (like Netflix, Disney+) need:
- User viewing behavior (billions of events)
- Content performance metrics
- Personalization algorithms
- A/B testing for UI changes

#### Iceberg for Streaming Analytics

```sql
-- Viewing events
CREATE TABLE lakehouse.viewing_events (
    user_id STRING,
    content_id STRING,
    event_type STRING,  -- play, pause, stop, skip
    timestamp TIMESTAMP,
    duration_seconds INT,
    device_type STRING,
    geo_location STRING,
    quality_level STRING,
    ab_test_variant STRING
)
USING iceberg
PARTITIONED BY (days(timestamp), geo_location)
TBLPROPERTIES (
    'write.metadata.delete-after-commit.enabled' = 'true'
);

-- Content performance analysis
SELECT
    content_id,
    COUNT(DISTINCT user_id) as unique_viewers,
    SUM(duration_seconds) / 3600 as total_hours_watched,
    AVG(duration_seconds) as avg_watch_time,
    SUM(CASE WHEN event_type = 'complete' THEN 1 ELSE 0 END) /
        COUNT(*) as completion_rate
FROM lakehouse.viewing_events
WHERE timestamp >= current_date - INTERVAL '7 days'
GROUP BY content_id
ORDER BY total_hours_watched DESC;
```

#### A/B Testing Analysis

```sql
-- Compare user engagement across test variants
SELECT
    ab_test_variant,
    COUNT(DISTINCT user_id) as users,
    AVG(duration_seconds) as avg_session_duration,
    SUM(duration_seconds) / COUNT(DISTINCT user_id) as avg_user_total_time
FROM lakehouse.viewing_events
WHERE timestamp >= current_date - INTERVAL '14 days'
    AND ab_test_variant IN ('control', 'variant_a', 'variant_b')
GROUP BY ab_test_variant;
```

#### Benefits
- **Performance**: Query billions of events in seconds
- **Flexibility**: Add new event types without schema migration
- **Cost**: 50% reduction in data warehouse costs
- **Speed**: A/B test results in real-time vs. next-day

---

## 4. Implementation Guide

### Step 1: Environment Setup

#### Option A: Local Development (Free)

```bash
# Install Spark with Iceberg support
pip install pyspark==3.5.0

# Download Iceberg runtime
wget https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/1.4.3/iceberg-spark-runtime-3.5_2.12-1.4.3.jar

# Start PySpark with Iceberg
pyspark \
  --packages org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.4.3 \
  --conf spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions \
  --conf spark.sql.catalog.lakehouse=org.apache.iceberg.spark.SparkCatalog \
  --conf spark.sql.catalog.lakehouse.type=hadoop \
  --conf spark.sql.catalog.lakehouse.warehouse=/tmp/iceberg-warehouse
```

#### Option B: AWS (Pay-as-you-go)

```python
# Configure Iceberg on AWS with S3
spark = SparkSession.builder \
    .appName("IcebergOnAWS") \
    .config("spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config("spark.sql.catalog.glue_catalog",
            "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.glue_catalog.warehouse",
            "s3://my-bucket/iceberg-warehouse") \
    .config("spark.sql.catalog.glue_catalog.catalog-impl",
            "org.apache.iceberg.aws.glue.GlueCatalog") \
    .config("spark.sql.catalog.glue_catalog.io-impl",
            "org.apache.iceberg.aws.s3.S3FileIO") \
    .getOrCreate()
```

#### Option C: Azure (Pay-as-you-go)

```python
# Configure Iceberg on Azure with ADLS
spark = SparkSession.builder \
    .config("spark.sql.catalog.lakehouse",
            "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.lakehouse.warehouse",
            "abfss://container@account.dfs.core.windows.net/iceberg") \
    .config("fs.azure.account.key.account.dfs.core.windows.net",
            "<storage-account-key>") \
    .getOrCreate()
```

### Step 2: Create Your First Iceberg Table

```python
from pyspark.sql import SparkSession
from pyspark.sql.types import *

# Sample data
data = [
    (1, "Alice", "Engineering", 100000, "2025-01-01"),
    (2, "Bob", "Sales", 80000, "2025-01-02"),
    (3, "Charlie", "Engineering", 95000, "2025-01-03")
]

schema = StructType([
    StructField("id", IntegerType(), False),
    StructField("name", StringType(), False),
    StructField("department", StringType(), True),
    StructField("salary", IntegerType(), True),
    StructField("hire_date", StringType(), True)
])

df = spark.createDataFrame(data, schema)

# Write to Iceberg table
df.writeTo("lakehouse.employees") \
    .using("iceberg") \
    .partitionedBy("department") \
    .createOrReplace()

# Query the table
spark.sql("SELECT * FROM lakehouse.employees").show()
```

### Step 3: Streaming Data Ingestion

```python
# Create streaming source (example with rate source)
streaming_df = spark.readStream \
    .format("rate") \
    .option("rowsPerSecond", 100) \
    .load()

# Transform
transformed_df = streaming_df.selectExpr(
    "value as id",
    "CAST(timestamp AS STRING) as event_time",
    "CAST(value % 10 AS STRING) as category"
)

# Write to Iceberg
query = transformed_df.writeStream \
    .format("iceberg") \
    .outputMode("append") \
    .trigger(processingTime="10 seconds") \
    .option("checkpointLocation", "/tmp/checkpoints/events") \
    .toTable("lakehouse.events")

query.awaitTermination()
```

### Step 4: Time Travel & Versioning

```python
# Query current data
current_df = spark.table("lakehouse.employees")

# Time travel to specific timestamp
historical_df = spark.read \
    .option("as-of-timestamp", "2025-01-01 00:00:00") \
    .table("lakehouse.employees")

# Time travel to specific snapshot
snapshot_df = spark.read \
    .option("snapshot-id", 12345678) \
    .table("lakehouse.employees")

# View all snapshots
spark.sql("""
    SELECT snapshot_id, committed_at, operation, summary
    FROM lakehouse.employees.snapshots
    ORDER BY committed_at DESC
""").show()

# Rollback to previous snapshot
spark.sql("""
    CALL lakehouse.system.rollback_to_snapshot('lakehouse.employees', 12345678)
""")
```

### Step 5: Schema Evolution

```python
# Add new columns
spark.sql("""
    ALTER TABLE lakehouse.employees
    ADD COLUMNS (
        email STRING,
        performance_rating FLOAT
    )
""")

# Rename column
spark.sql("""
    ALTER TABLE lakehouse.employees
    RENAME COLUMN salary TO annual_salary
""")

# Change partition strategy
spark.sql("""
    ALTER TABLE lakehouse.employees
    SET PARTITION SPEC (department, bucket(10, id))
""")
```

### Step 6: Maintenance Operations

```python
# Compact small files
spark.sql("""
    CALL lakehouse.system.rewrite_data_files('lakehouse.employees')
""")

# Remove old metadata
spark.sql("""
    CALL lakehouse.system.expire_snapshots('lakehouse.employees',
        TIMESTAMP '2025-01-01 00:00:00')
""")

# Remove orphan files
spark.sql("""
    CALL lakehouse.system.remove_orphan_files(
        table => 'lakehouse.employees',
        older_than => TIMESTAMP '2025-01-01 00:00:00'
    )
""")
```

---

## 5. Cost Analysis & ROI

### Total Cost of Ownership (TCO) Comparison

#### Scenario: 100 TB data, 1,000 queries/day

| Component | Traditional DW | Iceberg on Cloud | Savings |
|-----------|---------------|------------------|---------|
| **Storage** | $50K/month | $2.3K/month | 95% |
| **Compute** | $100K/month | $30K/month | 70% |
| **Licensing** | $50K/month | $0 | 100% |
| **Operations** | $20K/month | $5K/month | 75% |
| **TOTAL** | **$220K/month** | **$37.3K/month** | **83%** |

**Annual Savings**: $2.19M

### Storage Cost Breakdown

```
Traditional Data Warehouse (Snowflake/Redshift):
- 100 TB × $40/TB/month = $4,000/month base
- Replication (3x for HA) = $12,000/month
- Backup storage = $8,000/month
- Time travel storage = $30,000/month
Total: ~$50,000/month

Iceberg on S3:
- 100 TB × $23/TB/month (S3 Standard) = $2,300/month
- No replication fee (S3 built-in)
- Versioning included in Iceberg
Total: ~$2,300/month
```

### Compute Cost Comparison

```
Traditional DW:
- Always-on cluster: $100K/month
- Auto-scaling limited

Iceberg + Spark/Trino:
- On-demand clusters: $30K/month
- Scale to zero when idle
- Spot instances: 70% cheaper
```

### ROI Calculator

**Investment**:
- Implementation: $200K (4 months × $50K)
- Training: $20K
- Total: $220K

**Savings** (Annual):
- Storage: $575K
- Compute: $840K
- Licensing: $600K
- Operations: $180K
- Total: $2.19M

**ROI**: 900% in Year 1

**Payback Period**: 2 months

---

## 6. When to Use vs When NOT to Use

### ✅ Use Apache Iceberg When:

1. **Large-scale analytics** (100+ GB to petabytes)
2. **Need ACID transactions** on data lake
3. **Schema changes frequently** (evolving requirements)
4. **Multiple processing engines** (Spark, Flink, Trino, Dremio)
5. **Time travel/auditing required** (compliance, debugging)
6. **High concurrent writes** (many jobs writing simultaneously)
7. **Cost-sensitive** (want cheap object storage)
8. **Streaming + batch workloads** (lambda/kappa architecture)

### ❌ Do NOT Use Apache Iceberg When:

1. **Small datasets** (< 10 GB) - Use PostgreSQL/MySQL
2. **Transactional workload** (OLTP) - Use traditional RDBMS
3. **Sub-second latency required** - Use Cassandra/DynamoDB
4. **Simple key-value access** - Use Redis/DynamoDB
5. **No analytical queries** - Use operational database
6. **Team lacks Spark/data engineering skills** - Start with managed service
7. **Very high write throughput** (millions/sec) - Consider streaming DB

### Decision Matrix

| Requirement | Iceberg | Alternative |
|-------------|---------|-------------|
| Analytics on 1+ PB | ✅ Perfect | Snowflake ($$$$) |
| Real-time dashboards | ✅ Good | ClickHouse |
| OLTP (payments) | ❌ No | PostgreSQL |
| Key-value lookups | ❌ No | DynamoDB |
| 1-10 TB analytics | ✅ Good | BigQuery |
| < 100 GB | ❌ Overkill | PostgreSQL |
| Streaming analytics | ✅ Excellent | Kafka + Druid |
| Time-series IoT | ✅ Good | TimescaleDB |

---

## 7. Getting Started Checklist

### Week 1: Learning & POC
- [ ] Read Apache Iceberg documentation
- [ ] Install local Spark + Iceberg
- [ ] Create first Iceberg table
- [ ] Test time travel feature
- [ ] Benchmark query performance

### Week 2-3: Pilot Project
- [ ] Choose one business case (e.g., customer events)
- [ ] Design table schema
- [ ] Set up cloud storage (S3/Azure)
- [ ] Implement data ingestion
- [ ] Build analytics queries

### Week 4: Production Readiness
- [ ] Set up monitoring (Spark UI, Grafana)
- [ ] Implement compaction jobs
- [ ] Configure backup/disaster recovery
- [ ] Document data catalog
- [ ] Train team on operations

### Month 2-3: Scale & Optimize
- [ ] Add more data sources
- [ ] Optimize partitioning strategy
- [ ] Implement cost controls
- [ ] Build self-service analytics
- [ ] Measure ROI

---

## 8. Resources & Community

### Official Documentation
- **Apache Iceberg**: https://iceberg.apache.org
- **GitHub**: https://github.com/apache/iceberg
- **Slack**: https://apache-iceberg.slack.com

### Managed Services (Optional)
- **Tabular**: https://tabular.io (by Iceberg creators)
- **Dremio**: https://www.dremio.com
- **Databricks**: Iceberg support in Unity Catalog
- **AWS Glue**: Native Iceberg support
- **Snowflake**: Iceberg tables support

### Training & Certification
- **Dremio Iceberg Lakehouse Training** (Free)
- **Databricks Lakehouse Platform** (Paid)
- **Udemy**: Apache Iceberg courses
- **YouTube**: Iceberg Summit talks

### Books & Guides
- "Lakehouse Architecture with Apache Iceberg"
- "Data Engineering with Apache Spark and Iceberg"
- Netflix Tech Blog: Iceberg case studies

---

## 9. Conclusion

### Key Takeaways

1. **Free & Open Source**: Apache Iceberg is 100% free (Apache 2.0 license)
2. **Proven at Scale**: Used by Netflix, Apple, Adobe, LinkedIn (petabyte scale)
3. **Modern Use Cases**: CDP, financial analytics, IoT, healthcare, e-commerce
4. **Massive ROI**: 83% cost reduction, 900% ROI in Year 1
5. **Future-proof**: Vendor-neutral, works with all modern engines

### Why Iceberg in 2025?

The data landscape has shifted:
- **Old**: Proprietary data warehouses ($$$)
- **New**: Open lakehouse architecture (Iceberg)

**Benefits**:
- **Cost**: 10x cheaper than traditional DW
- **Flexibility**: Change schema without pain
- **Performance**: Query petabytes in seconds
- **Compliance**: Time travel for audits
- **Future-proof**: Open standard, no vendor lock-in

### Next Steps

1. **Start small**: Pick one use case
2. **POC in 1 week**: Test with sample data
3. **Measure**: Compare performance & cost
4. **Scale**: Expand to more data sources
5. **Optimize**: Fine-tune for your workload

**The future of data is open, scalable, and built on Apache Iceberg.**

---

*Document Version: 1.0*
*Last Updated: 2025-12-20*
*License: Apache 2.0*
