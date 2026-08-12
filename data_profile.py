from google.cloud import bigquery
import json
from datetime import date, datetime
from decimal import Decimal


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

PROJECT_ID = "vf-grp-gbissdbx-dev"
DATASET_ID = "ai_wireframe_dataset"
TABLE_ID = "sales_data"

OUTPUT_FILE = "data_profile.json"


# ---------------------------------------------------------
# BigQuery client
# ---------------------------------------------------------

client = bigquery.Client(project=PROJECT_ID)

table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"


# ---------------------------------------------------------
# Load table
# ---------------------------------------------------------

query = f"""
SELECT *
FROM `{table_ref}`
"""

df = client.query(query).to_dataframe()


# ---------------------------------------------------------
# Helper for JSON serialization
# ---------------------------------------------------------

def json_safe(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()

    if isinstance(value, Decimal):
        return float(value)

    return value


# ---------------------------------------------------------
# Get BigQuery schema
# ---------------------------------------------------------

table = client.get_table(table_ref)


# ---------------------------------------------------------
# Identify dimensions, measures and date dimensions
# ---------------------------------------------------------

dimensions = []
measures = []
date_dimensions = []

for field in table.schema:

    field_type = field.field_type.upper()

    if field_type in ["STRING", "DATE", "DATETIME", "TIMESTAMP"]:
        dimensions.append(field.name)

    if field_type in [
        "INTEGER",
        "INT64",
        "FLOAT",
        "FLOAT64",
        "NUMERIC",
        "BIGNUMERIC"
    ]:
        measures.append(field.name)

    if field_type in ["DATE", "DATETIME", "TIMESTAMP"]:
        date_dimensions.append(field.name)


# ---------------------------------------------------------
# Column-level profile
# ---------------------------------------------------------

columns = {}

for field in table.schema:

    column_name = field.name

    series = df[column_name]

    column_profile = {
        "name": column_name,
        "type": field.field_type,
        "mode": field.mode,
        "description": field.description,
        "null_count": int(series.isna().sum()),
        "distinct_count": int(series.nunique(dropna=True)),
    }

    # -------------------------
    # Numeric statistics
    # -------------------------

    if field.field_type.upper() in [
        "INTEGER",
        "INT64",
        "FLOAT",
        "FLOAT64",
        "NUMERIC",
        "BIGNUMERIC"
    ]:

        column_profile["statistics"] = {
            "min": json_safe(series.min()),
            "max": json_safe(series.max()),
            "mean": json_safe(series.mean()),
            "sum": json_safe(series.sum()),
        }

    # -------------------------
    # Categorical information
    # -------------------------

    if field.field_type.upper() == "STRING":

        values = (
            series
            .dropna()
            .astype(str)
            .value_counts()
            .head(10)
            .to_dict()
        )

        column_profile["top_values"] = values

    # -------------------------
    # Date information
    # -------------------------

    if field.field_type.upper() in [
        "DATE",
        "DATETIME",
        "TIMESTAMP"
    ]:

        non_null = series.dropna()

        if len(non_null) > 0:
            column_profile["date_range"] = {
                "min": json_safe(non_null.min()),
                "max": json_safe(non_null.max()),
            }

    columns[column_name] = column_profile


# ---------------------------------------------------------
# Sample rows
# ---------------------------------------------------------

sample_rows = df.head(10).to_dict(orient="records")

sample_rows = [
    {
        key: json_safe(value)
        for key, value in row.items()
    }
    for row in sample_rows
]


# ---------------------------------------------------------
# Final structured profile
# ---------------------------------------------------------

profile = {

    "dataset": {
        "project": PROJECT_ID,
        "dataset": DATASET_ID,
        "table": TABLE_ID,
        "table_reference": table_ref,
    },

    "summary": {
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
    },

    "dimensions": dimensions,

    "date_dimensions": date_dimensions,

    "measures": measures,

    "columns": columns,

    "sample_rows": sample_rows,
}


# ---------------------------------------------------------
# Save JSON
# ---------------------------------------------------------

with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    json.dump(
        profile,
        file,
        indent=2,
        ensure_ascii=False
    )


# ---------------------------------------------------------
# Terminal output
# ---------------------------------------------------------

print("=" * 60)
print("DATA PROFILE GENERATED")
print("=" * 60)

print(f"Table: {table_ref}")
print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")

print("\nDimensions:")
for item in dimensions:
    print(f"  - {item}")

print("\nDate dimensions:")
for item in date_dimensions:
    print(f"  - {item}")

print("\nMeasures:")
for item in measures:
    print(f"  - {item}")

print(f"\nStructured JSON saved to: {OUTPUT_FILE}")






python -c "from google.cloud import bigquery; c=bigquery.Client(project='vf-grp-gbissdbx-dev-1'); print('Client project:', c.project); print(c.query('SELECT 1 AS test').result().to_dataframe())"
python -c "from google.cloud import bigquery; c=bigquery.Client(project='vf-grp-gbissdbx-dev-1'); t=c.get_table('vf-grp-gbissdbx-dev-1.ai_wireframe_dataset.sales_data'); print('TABLE:', t.full_table_id); print('ROWS:', t.num_rows)"
 File "/home/abhisheks_s/ai_wireframe/backend/data_profile.py", line 36, in <module>
    df = client.query(query).to_dataframe()
         ^^^^^^^^^^^^^^^^^^^
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/google/cloud/bigquery/client.py", line 3624, in query
    return _job_helpers.query_jobs_insert(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/google/cloud/bigquery/_job_helpers.py", line 205, in query_jobs_insert
    future = do_query()
             ^^^^^^^^^^
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/google/api_core/retry/retry_unary.py", line 295, in retry_wrapped_func
    return retry_target(
           ^^^^^^^^^^^^^
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/google/api_core/retry/retry_unary.py", line 157, in retry_target
    next_sleep = _retry_error_helper(
                 ^^^^^^^^^^^^^^^^^^^^
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/google/api_core/retry/retry_base.py", line 215, in _retry_error_helper
    raise final_exc from source_exc
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/google/api_core/retry/retry_unary.py", line 148, in retry_target
    result = target()
             ^^^^^^^^
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/google/cloud/bigquery/_job_helpers.py", line 151, in do_query
    query_job._begin(retry=retry, timeout=timeout)
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/google/cloud/bigquery/job/query.py", line 1489, in _begin
    super(QueryJob, self)._begin(client=client, retry=retry, timeout=timeout)
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/google/cloud/bigquery/job/base.py", line 825, in _begin
    api_response = client._call_api(
                   ^^^^^^^^^^^^^^^^^
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/google/cloud/bigquery/client.py", line 895, in _call_api
    return call()
           ^^^^^^
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/google/api_core/retry/retry_unary.py", line 295, in retry_wrapped_func
    return retry_target(
           ^^^^^^^^^^^^^
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/google/api_core/retry/retry_unary.py", line 157, in retry_target
    next_sleep = _retry_error_helper(
                 ^^^^^^^^^^^^^^^^^^^^
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/google/api_core/retry/retry_base.py", line 215, in _retry_error_helper
    raise final_exc from source_exc
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/google/api_core/retry/retry_unary.py", line 148, in retry_target
    result = target()
             ^^^^^^^^
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/google/cloud/_http/__init__.py", line 494, in api_request
    raise exceptions.from_http_response(response)
google.api_core.exceptions.BadRequest: 400 POST https://bigquery.googleapis.com/bigquery/v2/projects/vf-grp-gbissdbx-dev/jobs?prettyPrint=false: ProjectId must be non-empty

Location: None
Job ID: 0ac41a82-c613-4e14-9ff3-83042634b431
