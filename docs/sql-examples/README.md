# Iceberg SQL Examples

This directory contains SQL query examples demonstrating Apache Iceberg capabilities including time travel, schema evolution, and snapshot management.

## Available Examples

1. **[Time Travel Queries](time-travel.sql)**: Query historical data using timestamps and snapshot IDs
2. **[Schema Evolution](schema-evolution.sql)**: Add, rename, and drop columns without rewriting data
3. **[Snapshot Management](snapshot-management.sql)**: Manage table snapshots, rollback, and cleanup
4. **[Partitioning Strategies](partitioning.sql)**: Hidden partitioning and partition evolution
5. **[Integration Examples](integration.sql)**: Combining Iceberg with SAP Graph and BDC data products

## Prerequisites

- Databricks Runtime 11.3+ or Spark 3.3+ with Iceberg support
- Iceberg Spark extensions configured
- Access to SAP BDC data products (for integration examples)

## Configuration

Add these Spark configurations to your session:

```python
spark.conf.set("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkCatalog")
spark.conf.set("spark.sql.catalog.spark_catalog.type", "hive")
spark.conf.set("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
```

## Key Iceberg Features

### Time Travel
Query data as it existed at a specific point in time using timestamps or snapshot IDs.

### Schema Evolution
Safely add, rename, or drop columns without expensive table rewrites.

### Snapshot Isolation
Read consistency across concurrent operations with ACID guarantees.

### Hidden Partitioning
Users don't need to know the partitioning scheme to write correct queries.

## Resources

- [Apache Iceberg Documentation](https://iceberg.apache.org/docs/latest/)
- [Iceberg SQL Reference](https://iceberg.apache.org/docs/latest/spark-queries/)
- [Databricks Iceberg Guide](https://docs.databricks.com/delta/uniform.html)
