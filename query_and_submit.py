import datetime as dt
import json
import os
import re
import requests
import subprocess
import yaml

metrics_token = os.environ.get("METRICS_WEBHOOK_TOKEN")

db_uri = (
    os.environ.get("DBURI")
    if "DBURI" in os.environ
    else (
        f"postgresql://{os.environ['DB_USER']}"
        f":{os.environ['DB_PASSWORD']}"
        f"@{os.environ['DB_HOST']}"
        f":{os.environ['DB_PORT']}"
        f"/{os.environ['DB_NAME']}"
    )
)

with open("/opt/config.yaml") as f:
    config = yaml.safe_load(f)

if "preExecuteScript" in config:
    os.system(config["preExecuteScript"])

one_hour_ago = dt.datetime.now() - dt.timedelta(hours=1)
interval_start = one_hour_ago.strftime("%Y-%m-%dT%H:00:00Z")
interval_end = one_hour_ago.strftime("%Y-%m-%dT%H:59:59Z")

metrics = {}

for metric_name, query in config["queries"].items():
    sql = query["countSql"]
    condition_keyword = "and" if re.search("where", sql, re.IGNORECASE) else "where"
    timestamp_col = query["timestampColumn"]
    metrics[metric_name] = json.loads(
        subprocess.check_output(
            [
                "psql",
                db_uri,
                "-Atc",
                f"{sql} {condition_keyword} \"{timestamp_col}\" between '{interval_start}' and '{interval_end}'",
            ]
        )
    )

response = requests.post(
    url=config["endpoint"],
    json={
        "startInterval": interval_start,
        "endInterval": interval_end,
        **metrics,
    },
    headers={
        "xc-token": metrics_token,
    },
)

if response.ok:
    print("export done")
else:
    print("export failed")
