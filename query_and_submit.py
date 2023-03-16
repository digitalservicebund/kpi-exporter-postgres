import datetime as dt
import json
import os
import re
import requests
import subprocess
import yaml

metrics_token = os.environ.get("METRICS_WEBHOOK_TOKEN")

with open("/opt/config.yaml") as f:
  config = yaml.safe_load(f)

if "preExecuteScript" in config:
  os.system(config["preExecuteScript"])

one_hour_ago = dt.datetime.now() - dt.timedelta(hours=1)
interval_start = one_hour_ago.strftime("%Y-%m-%dT%H:00:00Z")
interval_end = one_hour_ago.strftime("%Y-%m-%dT%H:59:59Z")

count_metrics = {}
metrics = []

for metric_name, query in config["queries"].items():
  count_sql = query.get("countSql")
  content_sql = query.get("contentSql")
  timestamp_col = query["timestampColumn"]
  
  if content_sql:
    condition_keyword = "and" if re.search("where", content_sql, re.IGNORECASE) else "where"
    db_result = subprocess.check_output(["psql", os.environ["DBURI"], "-Atc", f"{content_sql} {condition_keyword} \"{timestamp_col}\" between '{interval_start}' and '{interval_end}'"]).decode().split("\n")
    db_result = filter(lambda single_result: single_result != "", db_result)

    content_metric = {}

    for result in db_result:
      category, content, created_at = result.split("|")

      content_metric["category"] = category
      content_metric["content"] = content
      content_metric["date"] = created_at

      metrics.append({
        **content_metric
      })

  else:
    condition_keyword = "and" if re.search("where", count_sql, re.IGNORECASE) else "where"
    count_metrics[metric_name] = json.loads(subprocess.check_output(["psql", os.environ["DBURI"], "-Atc", f"{count_sql} {condition_keyword} \"{timestamp_col}\" between '{interval_start}' and '{interval_end}'"]))

if count_metrics:
  metrics.append({
    "startInterval": interval_start,
    "endInterval": interval_end,
    **count_metrics,
  })

requests.post(
  url=config["endpoint"],
  json=metrics,
  headers={
    "xc-token": metrics_token,
  }
)

if response.ok:
  print("export done")
else:
  print("export failed")
