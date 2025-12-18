# Microsoft Fabric Integration Architecture

## Overview

This architecture demonstrates how to consume SAP Business Data Cloud (BDC) data products in Microsoft Fabric using OneLake shortcuts and Iceberg compatibility for zero-copy data access.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      SAP Landscape                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ SAP S/4HANA  │  │ SAP Ariba    │  │  SAP Integration    │  │
│  │              │  │              │  │      Suite          │  │
│  │  (ERP Data)  │  │ (Procurement)│  │   (SAP Graph API)   │  │
│  └──────┬───────┘  └───────┬──────┘  └──────────┬───────────┘  │
│         │                  │                    │              │
│         └──────────────────┴────────────────────┘              │
│                            │                                    │
└────────────────────────────┼────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              SAP Business Data Cloud (BDC)                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         Data Products (Semantic Layer)                   │   │
│  │  - Curated datasets with business context                │   │
│  │  - Governed and quality-assured                          │   │
│  └────────────────────────┬─────────────────────────────────┘   │
│                           │                                     │
│  ┌────────────────────────┴─────────────────────────────────┐   │
│  │         Iceberg Tables on ADLS Gen2                      │   │
│  │  - Open table format  - Time travel  - Schema evolution  │   │
│  └────────────────────────┬─────────────────────────────────┘   │
│                           │                                     │
│                  Azure Data Lake Storage Gen2                   │
└────────────────────────────┼─────────────────────────────────────┘
                             │
                    ┌────────┴────────┐
                    │  OneLake        │
                    │  Shortcuts      │
                    └────────┬────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Microsoft Fabric                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  OneLake (Unified Storage)               │   │
│  │  - Single storage layer  - Auto data discovery           │   │
│  └────────────────────────┬─────────────────────────────────┘   │
│                           │                                     │
│  ┌────────────────────────┴─────────────────────────────────┐   │
│  │                   Lakehouse                              │   │
│  │  - SAP data via shortcuts  - Delta/Iceberg compatibility │   │
│  └──┬─────────────────┬─────────────────┬────────────────┬──┘   │
│     │                 │                 │                │      │
│  ┌──▼──────────┐  ┌───▼────────┐  ┌────▼───────┐  ┌────▼────┐ │
│  │   Synapse   │  │  Data      │  │  Power BI  │  │   ML    │ │
│  │  Analytics  │  │ Warehouse  │  │  Direct    │  │ Spark   │ │
│  │             │  │            │  │  Lake Mode │  │         │ │
│  └─────────────┘  └────────────┘  └────────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │   Downstream   │
                    │   Consumers    │
                    │ (Apps, Portals)│
                    └────────────────┘
```

## Components

### SAP Business Data Cloud (BDC)
- **Storage**: Azure Data Lake Storage Gen2
- **Format**: Apache Iceberg tables
- **Features**: Semantic modeling, governance, data products

### OneLake Shortcuts
- **Purpose**: Zero-copy data access to external storage
- **Features**:
  - No data movement or duplication
  - Automatic metadata discovery
  - Unified namespace
- **Supported Sources**: ADLS Gen2, S3, GCS, Dataverse

### Microsoft Fabric Lakehouse
- **Purpose**: Unified analytics workspace
- **Features**:
  - Delta Lake native with Iceberg compatibility
  - T-SQL and Spark endpoints
  - Power BI DirectLake mode
- **Integration**: Consumes SAP data via OneLake shortcuts

## Implementation Steps

### Step 1: Configure SAP BDC Storage on Azure

1. Ensure SAP BDC data is stored in ADLS Gen2:
   ```
   Storage Account: sapbdcstorage
   Container: data-products
   Path Structure:
     /finance/general_ledger/
     /sales/orders/
     /hr/employee_records/
   ```

2. Configure Iceberg table metadata:
   ```json
   {
     "format-version": 2,
     "table-uuid": "...",
     "location": "abfss://data-products@sapbdcstorage.dfs.core.windows.net/finance/general_ledger",
     "current-snapshot-id": 8734629847362
   }
   ```

### Step 2: Set Up Authentication

1. Create Service Principal in Azure AD:
   ```bash
   az ad sp create-for-rbac \
     --name "FabricSAPBDCIntegration" \
     --role "Storage Blob Data Contributor" \
     --scopes /subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.Storage/storageAccounts/sapbdcstorage
   ```

2. Grant Fabric workspace access:
   ```bash
   # Assign Storage Blob Data Reader role
   az role assignment create \
     --assignee <fabric-managed-identity> \
     --role "Storage Blob Data Reader" \
     --scope /subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.Storage/storageAccounts/sapbdcstorage
   ```

### Step 3: Create OneLake Shortcuts in Fabric

1. Navigate to Fabric Lakehouse
2. Create shortcut to SAP BDC storage:
   ```python
   # Using Fabric Python SDK
   from microsoft.fabric import FabricClient

   client = FabricClient()

   shortcut_config = {
       "name": "sap_finance_data",
       "path": "/SAP_BDC/finance",
       "target": {
           "type": "AdlsGen2",
           "endpoint": "https://sapbdcstorage.dfs.core.windows.net",
           "container": "data-products",
           "path": "finance/general_ledger",
           "authentication": {
               "type": "ServicePrincipal",
               "tenantId": "<tenant-id>",
               "clientId": "<client-id>",
               "clientSecret": "<client-secret>"
           }
       }
   }

   client.create_shortcut("lakehouse-id", shortcut_config)
   ```

3. Verify shortcut creation:
   ```sql
   -- List files in shortcut
   SELECT * FROM FILES('SAP_BDC/finance/');
   ```

### Step 4: Query SAP Data Products

1. Access data via T-SQL endpoint:
   ```sql
   -- Query Iceberg data through Fabric
   SELECT
       account_number,
       account_name,
       SUM(debit_amount) AS total_debits,
       SUM(credit_amount) AS total_credits
   FROM SAP_BDC.finance.general_ledger
   WHERE fiscal_year = 2025
   GROUP BY account_number, account_name;
   ```

2. Use Spark for advanced analytics:
   ```python
   # PySpark in Fabric notebook
   from pyspark.sql.functions import col, sum, avg

   # Read Iceberg table via shortcut
   gl_df = spark.read.format("iceberg") \
       .load("SAP_BDC/finance/general_ledger")

   # Perform analytics
   summary = (gl_df
       .filter(col("fiscal_year") == 2025)
       .groupBy("company_code", "fiscal_period")
       .agg(
           sum("debit_amount").alias("total_debits"),
           sum("credit_amount").alias("total_credits")
       ))

   summary.show()
   ```

### Step 5: Power BI DirectLake Integration

1. Create semantic model with DirectLake:
   ```python
   # Power BI semantic model definition
   {
     "name": "SAP Finance Analytics",
     "mode": "DirectLake",
     "tables": [
       {
         "name": "GeneralLedger",
         "source": {
           "type": "lakehouse",
           "table": "SAP_BDC.finance.general_ledger"
         }
       },
       {
         "name": "CostCenters",
         "source": {
           "type": "lakehouse",
           "table": "SAP_BDC.finance.cost_centers"
         }
       }
     ],
     "relationships": [
       {
         "from": "GeneralLedger[cost_center_id]",
         "to": "CostCenters[cost_center_id]"
       }
     ]
   }
   ```

2. Build Power BI report:
   ```dax
   // DAX measure for budget variance
   Budget Variance =
   VAR Actual = SUM(GeneralLedger[Amount])
   VAR Budget = SUM(Budget[BudgetAmount])
   RETURN Actual - Budget
   ```

### Step 6: Integrate SAP Graph API

1. Set up SAP BTP connection in Fabric:
   ```python
   import requests
   from pyspark.sql import SparkSession

   # Get OAuth token from SAP BTP
   token_url = "https://<tenant>.authentication.sap.hana.ondemand.com/oauth/token"
   token_response = requests.post(token_url, data={
       "grant_type": "client_credentials",
       "client_id": "<client-id>",
       "client_secret": "<client-secret>"
   })
   access_token = token_response.json()["access_token"]

   # Query SAP Graph
   graph_url = "https://graph.sap/v1/SalesOrders"
   headers = {"Authorization": f"Bearer {access_token}"}
   response = requests.get(graph_url, headers=headers)

   # Load into Spark DataFrame
   graph_data = spark.read.json(sc.parallelize([response.text]))

   # Enrich with SAP BDC data
   bdc_orders = spark.read.format("iceberg") \
       .load("SAP_BDC/sales/orders")

   enriched = bdc_orders.join(graph_data, "order_id", "left")
   ```

## Best Practices

### Performance Optimization

1. **Use DirectLake Mode**
   - Eliminate import and DirectQuery overhead
   - Query data directly from OneLake
   - Automatic refresh as data changes

2. **Optimize File Layout**
   ```python
   # Compact Iceberg files for better performance
   from delta.tables import DeltaTable

   # Convert to Delta if needed for Fabric optimization
   (spark.read.format("iceberg")
    .load("SAP_BDC/finance/general_ledger")
    .write.format("delta")
    .mode("overwrite")
    .save("optimized/finance/general_ledger"))
   ```

3. **Partition Strategy**
   ```sql
   -- Leverage Iceberg partitioning
   SELECT * FROM SAP_BDC.finance.general_ledger
   WHERE fiscal_year = 2025
     AND fiscal_period = 3
     AND company_code = '1000';
   ```

### Data Governance

1. **Microsoft Purview Integration**
   ```python
   # Register SAP data products in Purview
   from azure.purview.catalog import PurviewCatalogClient

   client = PurviewCatalogClient(
       endpoint="https://<purview-account>.purview.azure.com",
       credential=credential
   )

   # Create asset for SAP data product
   asset = {
       "typeName": "azure_datalake_gen2_resource_set",
       "attributes": {
           "qualifiedName": "sapbdcstorage/data-products/finance/general_ledger",
           "name": "SAP Finance General Ledger",
           "description": "General ledger data from SAP S/4HANA"
       }
   }

   client.entity.create_or_update(asset)
   ```

2. **Sensitivity Labels**
   ```sql
   -- Apply sensitivity classification
   ALTER TABLE SAP_BDC.hr.employee_records
   SET CLASSIFICATION 'Highly Confidential';
   ```

### Cost Optimization

1. **OneLake Shortcuts Benefits**
   - Zero data copy costs
   - No egress charges within Azure region
   - Storage billed only once (in SAP BDC)

2. **Compute Optimization**
   - Use serverless SQL for ad-hoc queries
   - Schedule Spark jobs during off-peak hours
   - Enable auto-pause for idle resources

3. **Capacity Management**
   ```python
   # Monitor capacity usage
   from microsoft.fabric.monitoring import CapacityMetrics

   metrics = CapacityMetrics()
   usage = metrics.get_capacity_usage(capacity_id="<capacity-id>")
   print(f"CU consumption: {usage.compute_units}")
   ```

## Security & Compliance

### Row-Level Security

```sql
-- Define RLS in Fabric
CREATE SECURITY POLICY CompanyCodeRLS
ADD FILTER PREDICATE dbo.fn_CompanyCodeFilter(company_code)
ON SAP_BDC.finance.general_ledger
WITH (STATE = ON);

-- Filter function
CREATE FUNCTION dbo.fn_CompanyCodeFilter(@CompanyCode NVARCHAR(10))
RETURNS TABLE
WITH SCHEMABINDING
AS
RETURN SELECT 1 AS result
WHERE @CompanyCode IN (
    SELECT company_code
    FROM dbo.UserCompanyCodeMapping
    WHERE user_email = USER_NAME()
);
```

### Encryption

1. **Data at Rest**: Enabled by default in OneLake
2. **Data in Transit**: TLS 1.2+ for all connections
3. **Customer-Managed Keys**: Configure in Azure Key Vault

```python
# Configure CMK for OneLake
from azure.mgmt.fabric import FabricManagementClient

fabric_client = FabricManagementClient(credential, subscription_id)

encryption_config = {
    "keyVaultKeyUri": "https://<keyvault>.vault.azure.net/keys/<key-name>",
    "managedIdentity": {
        "userAssignedIdentity": "<managed-identity-id>"
    }
}

fabric_client.workspaces.update_encryption(
    workspace_id="<workspace-id>",
    encryption=encryption_config
)
```

## Monitoring & Troubleshooting

### Query Performance

```sql
-- View query execution plans
SET STATISTICS PROFILE ON;

SELECT * FROM SAP_BDC.finance.general_ledger
WHERE fiscal_year = 2025;

-- Check table statistics
DBCC SHOW_STATISTICS('SAP_BDC.finance.general_ledger', fiscal_year);
```

### Shortcut Health

```python
# Monitor shortcut status
from microsoft.fabric import FabricClient

client = FabricClient()
shortcuts = client.list_shortcuts(lakehouse_id="<lakehouse-id>")

for shortcut in shortcuts:
    print(f"Name: {shortcut.name}, Status: {shortcut.status}")
    if shortcut.status != "Active":
        print(f"Error: {shortcut.error_message}")
```

### Data Lineage

```sql
-- View lineage in Purview
SELECT
    entity_name,
    entity_type,
    source_system,
    lineage_path
FROM purview.lineage
WHERE entity_name LIKE '%general_ledger%';
```

## Example Use Cases

### Financial Consolidation

```sql
-- Multi-company consolidation report
WITH company_totals AS (
    SELECT
        company_code,
        fiscal_year,
        fiscal_period,
        SUM(debit_amount) AS total_debits,
        SUM(credit_amount) AS total_credits
    FROM SAP_BDC.finance.general_ledger
    WHERE fiscal_year = 2025
    GROUP BY company_code, fiscal_year, fiscal_period
)
SELECT
    fiscal_year,
    fiscal_period,
    SUM(total_debits) AS consolidated_debits,
    SUM(total_credits) AS consolidated_credits,
    SUM(total_debits) - SUM(total_credits) AS net_position
FROM company_totals
GROUP BY fiscal_year, fiscal_period
ORDER BY fiscal_year, fiscal_period;
```

### HR Workforce Analytics

```python
# Combine SAP HR data with Microsoft 365 activity
from pyspark.sql.functions import col, datediff, current_date

# SAP employee data via shortcut
employees_df = spark.read.format("iceberg") \
    .load("SAP_BDC/hr/employee_records")

# Microsoft Graph data (Teams, email activity)
# Assume fetched separately
m365_activity = spark.table("microsoft_graph.user_activity")

# Combined analytics
workforce_insights = (employees_df
    .join(m365_activity, employees_df.email == m365_activity.user_principal_name, "left")
    .withColumn("tenure_days", datediff(current_date(), col("hire_date")))
    .select(
        "employee_id",
        "employee_name",
        "department",
        "tenure_days",
        "email_count",
        "teams_messages_count",
        "meeting_hours"
    ))

workforce_insights.write.format("delta").saveAsTable("analytics.workforce_insights")
```

## Resources

- [Microsoft Fabric Documentation](https://learn.microsoft.com/en-us/fabric/)
- [OneLake Shortcuts Guide](https://learn.microsoft.com/en-us/fabric/onelake/onelake-shortcuts)
- [DirectLake Mode](https://learn.microsoft.com/en-us/power-bi/enterprise/directlake-overview)
- [SAP BDC on Azure](https://help.sap.com/docs/sap-datasphere)
