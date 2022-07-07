Collect KPIs from a PostgreSQL database and send them to a metrics endpoint.

Requires a config in this form:

```yaml
---
endpoint: "https://your-metrics-endpoint"
queries:
  metric1:
    countSql: 'select count(*) from "User"'
    timestampColumn: createdAt
```

Set the `DBURI` environment variable to a connection string libpq recognises.
