import datetime as dt
import json
import os
import re
import requests
import subprocess
import yaml


def read_secret_file(key):
    try:
        with open(key, "r") as secret_file:
            return secret_file.read().strip()
    except Exception as e:
        raise SecretReadError(f"Error reading secret from {filepath}: {str(e)}")


with open("/opt/config.yaml") as f:
    config = yaml.safe_load(f)

metrics_token = read_secret_file(config["endpoint-token-secret-file"])

db_uri = (
    os.environ.get("DBURI")
    if "DBURI" in os.environ
    else (
        f"postgresql://{read_secret_file(config['db']['user-secret-file'])}"
        f":{read_secret_file(config['db']['password-secret-file'])}"
        f"@{config['db']['host']}"
        f":{config['db']['port']}"
        f"/{config['db']['name']}"
    )
)

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
