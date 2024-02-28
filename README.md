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

In order to connect with a db configure how to connect (User and secret should point to a mounted secret):

```yaml
db:
  host: localhost
  port: 5432
  name: database-name
  user-secret-file: /mounted-secret-path/database-user
  password-secret-file: /mounted-secret-path/database-password
```

Alternatively, set the `DBURI` environment variable to a connection string libpq recognises.

This script assumes to be scheduled hourly. It collects data for defined queries for the last hour. So you probably want to use it with a cronjob like this:

```yaml
---
kind: CronJob
spec:
  schedule: "1 * * * *"
```
