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

This script assumes to be scheduled hourly. It collects data for defined queries for the last hour. So you probably want to use it with a cronjob like this:

```yaml
---
kind: CronJob
spec:
  schedule: "1 * * * *"
```
