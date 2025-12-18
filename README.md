# Open + Semantic Data Stack

This project outlines how Apache Iceberg, SAP Business Data Cloud, and Graph APIs interoperate to deliver an open, semantic data foundation.

## Core Components

- **Apache Iceberg**: Open table format for data lakes with schema evolution, time travel, and snapshot isolation.
- **SAP Business Data Cloud (BDC)**: Publishes semantically rich SAP data products and supports zero-copy sharing across ecosystems such as Databricks and Microsoft Fabric.
- **Graph APIs**: SAP Graph for navigating business objects via OData v4 or GraphQL, and external options like Microsoft Graph for collaboration and workflow automation.

## Why the Combination Works

1. **Open storage + governance**: Iceberg ensures reliable table semantics on top of data lake files, enabling analytics changes without sacrificing historical integrity.
2. **Semantic richness**: BDC standardizes business meaning so downstream consumers receive curated, governed datasets rather than raw tables.
3. **Graph-enabled context**: Graph APIs expose connected business objects, reducing integration plumbing and accelerating application development.

## Example Use Cases

### Finance
Reconcile ledgers with time-travel queries against Iceberg tables while keeping SAP source-of-truth semantics intact.

### HR
Blend SAP HR data products with external workforce datasets for analytics without copying sensitive records.

### Supply Chain
Land IoT telemetry into Iceberg, join with SAP delivery and logistics objects via SAP Graph, and share unified insights with partners through zero-copy data products.

## Integration Overview

1. **Land raw and curated data** into Iceberg-backed tables to gain schema evolution and snapshot capabilities.
2. **Publish SAP datasets** as BDC data products, then expose them for zero-copy consumption in engines such as Databricks or Microsoft Fabric.
3. **Leverage SAP Graph** or external Graph APIs to traverse related business entities (e.g., orders, shipments, employees) and enrich analytics pipelines or applications.
4. **Use time-travel queries** for auditing and reconciliation scenarios that require point-in-time views of data.

## Getting Started

### Documentation Structure

- **[Connection Templates](docs/connection-templates/)**: SAP BTP destinations and Graph API configurations
- **[SQL Examples](docs/sql-examples/)**: Iceberg time travel and schema evolution queries
- **[Reference Architectures](docs/architectures/)**: Databricks and Microsoft Fabric integration patterns

## Key Technologies

- **Apache Iceberg**: [iceberg.apache.org](https://iceberg.apache.org)
- **SAP Business Data Cloud**: Zero-copy sharing to Databricks and Microsoft Fabric
- **SAP Graph**: OData v4 / GraphQL for business object navigation via [SAP Integration Suite](https://help.sap.com/docs/integration-suite)
- **Microsoft Graph**: External collaboration automation via SAP BTP destinations

## Benefits

- **Audit-friendly**: Time travel capabilities for compliance and historical analysis
- **Semantic governance**: Business meaning preserved from SAP through to analytics
- **Zero-copy sharing**: Efficient data distribution without duplication
- **Reduced integration complexity**: Graph APIs minimize custom plumbing
- **Multi-cloud ready**: Works across Databricks, Microsoft Fabric, and other platforms

## Tags

`#ApacheIceberg` `#SAPBTP` `#SAPBusinessDataCloud` `#Lakehouse` `#DataProducts` `#GraphQL` `#SAPGraph` `#Databricks` `#MicrosoftFabric`

## Contributing

This repository serves as a reference implementation and documentation hub. Contributions welcome for:
- Additional connection templates
- Real-world use case examples
- Performance optimization patterns
- Integration best practices

## License

See LICENSE file for details.
