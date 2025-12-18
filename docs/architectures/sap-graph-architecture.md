# SAP Graph Integration Architecture

## Overview

This architecture demonstrates how to combine SAP Graph APIs with Apache Iceberg analytics for enriched, context-aware data processing. SAP Graph provides relationship navigation across SAP business objects while Iceberg enables historical analysis and auditability.

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                       SAP Systems                                │
│  ┌───────────┐  ┌────────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ S/4HANA   │  │  Success   │  │ Ariba    │  │  Concur      │  │
│  │           │  │  Factors   │  │          │  │              │  │
│  │  Orders   │  │  Employees │  │ Suppliers│  │  Expenses    │  │
│  │  Products │  │  Org Units │  │ Contracts│  │  Receipts    │  │
│  └─────┬─────┘  └──────┬─────┘  └────┬─────┘  └──────┬───────┘  │
│        │               │             │               │          │
│        └───────────────┴─────────────┴───────────────┘          │
│                        │                                         │
└────────────────────────┼─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│              SAP Integration Suite (Graph)                       │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │               SAP Graph Business Objects                   │  │
│  │  - Unified business data model                             │  │
│  │  - Relationship navigation                                 │  │
│  │  - OData v4 & GraphQL endpoints                            │  │
│  └──────┬───────────────────────────────────────┬─────────────┘  │
│         │                                       │                │
│    ┌────▼───────┐                      ┌────────▼────────┐       │
│    │  OData v4  │                      │    GraphQL      │       │
│    │  Endpoint  │                      │    Endpoint     │       │
│    └────────────┘                      └─────────────────┘       │
└──────────────────────────────────────────────────────────────────┘
         │                                       │
         └───────────────┬───────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│                Integration & Enrichment Layer                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │         API Gateway / Data Pipeline                        │  │
│  │  - Authentication & authorization                          │  │
│  │  - Rate limiting & throttling                              │  │
│  │  - Response caching                                        │  │
│  │  - Data transformation                                     │  │
│  └──────┬─────────────────────────────────────────────────────┘  │
└─────────┼────────────────────────────────────────────────────────┘
          │
          ▼
┌──────────────────────────────────────────────────────────────────┐
│                  SAP Business Data Cloud                         │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │              Iceberg Tables (Historical Data)              │  │
│  │  - Time-series snapshots of SAP Graph data                 │  │
│  │  - Historical relationship graphs                          │  │
│  │  - Audit trails and change tracking                        │  │
│  └──────┬─────────────────────────────────────────────────────┘  │
└─────────┼────────────────────────────────────────────────────────┘
          │
          ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Analytics Platform                            │
│           (Databricks / Microsoft Fabric / Spark)                │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │          Hybrid Query Engine                               │  │
│  │  - Real-time: SAP Graph API calls                          │  │
│  │  - Historical: Iceberg time travel queries                 │  │
│  │  - Combined: Enriched analytics with context               │  │
│  └──────┬─────────────────────────────────────────────────────┘  │
│         │                                                        │
│  ┌──────▼─────────────────────────────────────────────────────┐  │
│  │              Analytics Workloads                           │  │
│  │  - Customer 360  - Supply chain visibility                 │  │
│  │  - Finance reconciliation  - HR insights                   │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

## SAP Graph Fundamentals

### Business Object Model

SAP Graph provides a unified business data model across SAP products:

```graphql
# GraphQL Schema Example
type SalesOrder {
  id: ID!
  orderNumber: String!
  orderDate: DateTime!
  customer: Customer!
  orderItems: [OrderItem!]!
  totalAmount: Decimal!
  currency: String!
  status: OrderStatus!
  deliveries: [Delivery!]!
}

type Customer {
  id: ID!
  customerNumber: String!
  name: String!
  segment: String!
  creditLimit: Decimal!
  orders: [SalesOrder!]!
  contactPerson: Employee
}

type OrderItem {
  id: ID!
  position: Int!
  product: Product!
  quantity: Decimal!
  unitPrice: Decimal!
  salesOrder: SalesOrder!
}
```

### Relationship Navigation

Navigate connected business objects without complex joins:

```graphql
# Get customer with all related data in single query
query CustomerContext {
  customer(id: "CUST-12345") {
    name
    segment
    orders(filter: { orderDate: { gte: "2025-01-01" } }) {
      orderNumber
      totalAmount
      orderItems {
        product {
          productName
          category
        }
        quantity
      }
      deliveries {
        deliveryDate
        status
      }
    }
    contactPerson {
      name
      email
      department
    }
  }
}
```

## Integration Patterns

### Pattern 1: Real-Time Enrichment

Enrich Iceberg analytics with real-time SAP Graph data:

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf
from pyspark.sql.types import StructType, StructField, StringType, DecimalType
import requests

spark = SparkSession.builder.appName("SAP_Graph_Enrichment").getOrCreate()

# Define SAP Graph API client
class SAPGraphClient:
    def __init__(self, base_url, client_id, client_secret):
        self.base_url = base_url
        self.token = self._get_token(client_id, client_secret)

    def _get_token(self, client_id, client_secret):
        # OAuth token retrieval
        token_url = f"{self.base_url}/oauth/token"
        response = requests.post(token_url, data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret
        })
        return response.json()["access_token"]

    def get_customer(self, customer_id):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(
            f"{self.base_url}/v1/customers/{customer_id}",
            headers=headers
        )
        return response.json() if response.ok else None

# Create client
graph_client = SAPGraphClient(
    base_url="https://graph.sap",
    client_id=dbutils.secrets.get("sap", "client-id"),
    client_secret=dbutils.secrets.get("sap", "client-secret")
)

# Define UDF for enrichment
schema = StructType([
    StructField("customer_name", StringType(), True),
    StructField("customer_segment", StringType(), True),
    StructField("credit_limit", DecimalType(18, 2), True)
])

@udf(returnType=schema)
def enrich_with_graph(customer_id):
    data = graph_client.get_customer(customer_id)
    if data:
        return (data["name"], data["segment"], data["creditLimit"])
    return (None, None, None)

# Read historical orders from Iceberg
orders_df = spark.table("sap_bdc.sales.orders")

# Enrich with real-time customer data
enriched_df = orders_df \
    .withColumn("customer_info", enrich_with_graph(col("customer_id"))) \
    .select(
        "order_id",
        "order_date",
        "customer_id",
        col("customer_info.customer_name").alias("customer_name"),
        col("customer_info.customer_segment").alias("segment"),
        "order_amount"
    )

enriched_df.show()
```

### Pattern 2: Historical Graph Snapshots

Capture SAP Graph state over time in Iceberg:

```python
from datetime import datetime
from pyspark.sql.functions import lit, current_timestamp

# Fetch current state from SAP Graph
def capture_graph_snapshot(entity_type, graph_client):
    """Capture snapshot of SAP Graph entities"""

    # Fetch entities from Graph API
    if entity_type == "customers":
        endpoint = "/v1/customers"
    elif entity_type == "products":
        endpoint = "/v1/products"
    else:
        raise ValueError(f"Unknown entity type: {entity_type}")

    headers = {"Authorization": f"Bearer {graph_client.token}"}
    response = requests.get(f"{graph_client.base_url}{endpoint}", headers=headers)

    entities = response.json().get("value", [])

    # Convert to DataFrame
    df = spark.createDataFrame(entities)

    # Add snapshot metadata
    df_with_metadata = df \
        .withColumn("snapshot_timestamp", current_timestamp()) \
        .withColumn("source_system", lit("SAP_GRAPH"))

    # Append to Iceberg table
    df_with_metadata.writeTo(f"sap_bdc.snapshots.{entity_type}") \
        .using("iceberg") \
        .append()

    return df_with_metadata

# Schedule periodic snapshots
snapshot_df = capture_graph_snapshot("customers", graph_client)
print(f"Captured {snapshot_df.count()} customer records")
```

### Pattern 3: Time Travel Comparison

Compare historical Iceberg data with current Graph state:

```sql
-- Compare customer data: yesterday vs today
WITH iceberg_snapshot AS (
    SELECT
        customer_id,
        customer_name,
        credit_limit,
        customer_segment
    FROM sap_bdc.snapshots.customers
    FOR SYSTEM_TIME AS OF CURRENT_TIMESTAMP - INTERVAL 1 DAY
),
graph_current AS (
    SELECT
        customer_id,
        customer_name,
        credit_limit,
        customer_segment
    FROM sap_bdc.snapshots.customers
)
SELECT
    i.customer_id,
    i.customer_name,
    i.credit_limit AS yesterday_credit_limit,
    g.credit_limit AS current_credit_limit,
    g.credit_limit - i.credit_limit AS credit_limit_change,
    i.customer_segment AS yesterday_segment,
    g.customer_segment AS current_segment
FROM iceberg_snapshot i
FULL OUTER JOIN graph_current g ON i.customer_id = g.customer_id
WHERE i.credit_limit != g.credit_limit
   OR i.customer_segment != g.customer_segment;
```

### Pattern 4: Graph Traversal with Analytics

Navigate relationships and aggregate analytics:

```python
# GraphQL query to traverse order -> items -> products
graphql_query = """
query OrderProductAnalytics($startDate: DateTime!) {
  salesOrders(filter: { orderDate: { gte: $startDate } }) {
    orderNumber
    orderDate
    customer {
      customerNumber
      segment
    }
    orderItems {
      quantity
      unitPrice
      product {
        productId
        productName
        category
        supplier {
          supplierName
          country
        }
      }
    }
  }
}
"""

# Execute GraphQL query
response = requests.post(
    f"{graph_client.base_url}/graphql",
    headers={
        "Authorization": f"Bearer {graph_client.token}",
        "Content-Type": "application/json"
    },
    json={
        "query": graphql_query,
        "variables": {"startDate": "2025-01-01T00:00:00Z"}
    }
)

graph_data = response.json()["data"]["salesOrders"]

# Flatten nested structure
from pyspark.sql.functions import explode

# Convert to DataFrame
raw_df = spark.createDataFrame(graph_data)

# Flatten order items and products
orders_flattened = raw_df \
    .select(
        col("orderNumber"),
        col("orderDate"),
        col("customer.customerNumber").alias("customer_number"),
        col("customer.segment").alias("customer_segment"),
        explode("orderItems").alias("item")
    ) \
    .select(
        "orderNumber",
        "orderDate",
        "customer_number",
        "customer_segment",
        col("item.quantity"),
        col("item.unitPrice"),
        col("item.product.productName").alias("product_name"),
        col("item.product.category").alias("product_category"),
        col("item.product.supplier.country").alias("supplier_country")
    )

# Aggregate by product category and supplier country
category_analysis = orders_flattened \
    .groupBy("product_category", "supplier_country") \
    .agg(
        count("orderNumber").alias("order_count"),
        sum(col("quantity") * col("unitPrice")).alias("total_revenue")
    ) \
    .orderBy(col("total_revenue").desc())

category_analysis.show()
```

## Use Cases

### Use Case 1: Customer 360 View

Combine historical behavior (Iceberg) with current state (Graph):

```python
from pyspark.sql.functions import col, sum, count, max, lit

# Historical order analytics from Iceberg
historical_orders = spark.table("sap_bdc.sales.orders") \
    .groupBy("customer_id") \
    .agg(
        count("order_id").alias("lifetime_orders"),
        sum("order_amount").alias("lifetime_value"),
        max("order_date").alias("last_order_date")
    )

# Current customer details from Graph API
def get_graph_customers():
    response = requests.get(
        f"{graph_client.base_url}/v1/customers",
        headers={"Authorization": f"Bearer {graph_client.token}"}
    )
    return spark.createDataFrame(response.json()["value"])

current_customers = get_graph_customers() \
    .select(
        col("id").alias("customer_id"),
        "customerNumber",
        "name",
        "segment",
        "creditLimit",
        "paymentTerms"
    )

# Customer 360 view
customer_360 = current_customers \
    .join(historical_orders, "customer_id", "left") \
    .withColumn("lifetime_orders", coalesce("lifetime_orders", lit(0))) \
    .withColumn("lifetime_value", coalesce("lifetime_value", lit(0.0)))

customer_360.write.format("delta").mode("overwrite").saveAsTable("analytics.customer_360")
```

### Use Case 2: Supply Chain Traceability

Track products through the supply chain using Graph relationships:

```graphql
query SupplyChainTrace($productId: ID!) {
  product(id: $productId) {
    productId
    productName
    supplier {
      supplierName
      country
      contracts {
        contractNumber
        validFrom
        validTo
      }
    }
    orderItems {
      salesOrder {
        orderNumber
        customer {
          name
        }
        deliveries {
          deliveryNumber
          plannedDeliveryDate
          actualDeliveryDate
          shipments {
            trackingNumber
            carrier
            status
          }
        }
      }
    }
    qualityInspections {
      inspectionDate
      result
      inspector {
        name
      }
    }
  }
}
```

### Use Case 3: Financial Reconciliation

Reconcile GL entries (Iceberg) with live SAP state (Graph):

```sql
-- Compare posted documents in Iceberg vs SAP Graph
WITH iceberg_documents AS (
    SELECT
        document_number,
        posting_date,
        company_code,
        SUM(amount) AS iceberg_total
    FROM sap_bdc.finance.general_ledger
    WHERE posting_date = CURRENT_DATE - INTERVAL 1 DAY
    GROUP BY document_number, posting_date, company_code
),
graph_documents AS (
    SELECT
        document_number,
        posting_date,
        company_code,
        total_amount AS graph_total
    FROM sap_graph.accounting_documents
    WHERE posting_date = CURRENT_DATE - INTERVAL 1 DAY
)
SELECT
    COALESCE(i.document_number, g.document_number) AS document_number,
    i.iceberg_total,
    g.graph_total,
    ABS(COALESCE(i.iceberg_total, 0) - COALESCE(g.graph_total, 0)) AS variance,
    CASE
        WHEN i.document_number IS NULL THEN 'Missing in Iceberg'
        WHEN g.document_number IS NULL THEN 'Missing in Graph'
        WHEN ABS(i.iceberg_total - g.graph_total) > 0.01 THEN 'Amount Mismatch'
        ELSE 'OK'
    END AS reconciliation_status
FROM iceberg_documents i
FULL OUTER JOIN graph_documents g
    ON i.document_number = g.document_number
WHERE COALESCE(i.iceberg_total, 0) != COALESCE(g.graph_total, 0);
```

## Best Practices

### API Rate Limiting

```python
from time import sleep
from functools import wraps

def rate_limit(max_calls=100, period=60):
    """Decorator to rate limit Graph API calls"""
    calls = []

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            # Remove calls older than period
            calls[:] = [c for c in calls if c > now - period]

            if len(calls) >= max_calls:
                sleep_time = period - (now - calls[0])
                if sleep_time > 0:
                    sleep(sleep_time)
                calls[:] = []

            calls.append(time.time())
            return func(*args, **kwargs)
        return wrapper
    return decorator

@rate_limit(max_calls=100, period=60)
def call_sap_graph(endpoint):
    response = requests.get(
        f"{graph_client.base_url}{endpoint}",
        headers={"Authorization": f"Bearer {graph_client.token}"}
    )
    return response.json()
```

### Caching Strategy

```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedGraphClient:
    def __init__(self, graph_client, cache_ttl_seconds=300):
        self.graph_client = graph_client
        self.cache_ttl = cache_ttl_seconds
        self.cache = {}

    def get_entity(self, entity_type, entity_id):
        cache_key = f"{entity_type}:{entity_id}"
        now = datetime.now()

        # Check cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if (now - timestamp).total_seconds() < self.cache_ttl:
                return cached_data

        # Fetch from API
        data = self.graph_client.get_customer(entity_id)
        self.cache[cache_key] = (data, now)
        return data
```

### Error Handling

```python
from requests.exceptions import RequestException
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def resilient_graph_call(endpoint, graph_client):
    """Call SAP Graph with automatic retry"""
    try:
        response = requests.get(
            f"{graph_client.base_url}{endpoint}",
            headers={"Authorization": f"Bearer {graph_client.token}"},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        print(f"Graph API call failed: {e}")
        raise
```

## Resources

- [SAP Graph Documentation](https://help.sap.com/docs/graph)
- [SAP Graph API Reference](https://api.sap.com/graph)
- [GraphQL Best Practices](https://graphql.org/learn/best-practices/)
- [OData v4 Specification](https://www.odata.org/documentation/)
