# Connection Templates

This directory contains templates for connecting to SAP BTP destinations and Graph APIs.

## Available Templates

1. **[SAP BTP Destination](sap-btp-destination.json)**: Configuration for SAP Business Technology Platform destinations
2. **[SAP Graph Configuration](sap-graph-config.json)**: Setup for SAP Graph API connections
3. **[Microsoft Graph](microsoft-graph-config.json)**: Microsoft Graph API integration via BTP
4. **[Databricks Connection](databricks-config.json)**: Databricks workspace connection for BDC data products
5. **[Microsoft Fabric](fabric-config.json)**: Microsoft Fabric connection for zero-copy sharing

## General Setup Steps

1. Configure authentication credentials
2. Set up destination properties
3. Test connectivity
4. Enable data product consumption (for BDC connections)
5. Configure Graph API scopes and permissions

## Security Best Practices

- Store credentials in secure vaults (SAP Credential Store, Azure Key Vault, etc.)
- Use OAuth 2.0 flows for API authentication
- Rotate credentials regularly
- Apply principle of least privilege for API scopes
- Enable audit logging for all connections

## Support

Refer to official documentation:
- [SAP BTP Destinations](https://help.sap.com/docs/connectivity/sap-btp-connectivity-cf/http-destinations)
- [SAP Graph](https://help.sap.com/docs/graph)
- [Microsoft Graph](https://learn.microsoft.com/en-us/graph/overview)
