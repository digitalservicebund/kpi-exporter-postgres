Collect KPIs from a PostgreSQL database and send them to a metrics endpoint.

Requires a config in this form:

```yaml
---
endpoint: "https://your-metrics-endpoint" #Make sure to use the bulk endpoint
queries:
  metric1:
    countSql: 'select count(*) from "User"'
    timestampColumn: createdAt
```

Set the `DBURI` environment variable to a connection string libpq recognises.

If you want to send content data to a metrics endpoint you can use a config like this (make sure that the table has a category, date and content column):
```yaml
---
endpoint: "https://your-metrics-endpoint" #Make sure to use the bulk endpoint
queries:
  metric1:
    contentSql: 'select * from "Survey"'
    timestampColumn: createdAt
```
