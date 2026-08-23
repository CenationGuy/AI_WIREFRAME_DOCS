import json
import pandas as pd
from google.cloud import bigquery


# =========================================================
# CONFIGURATION
# =========================================================

PROJECT_ID = "vf-grp-gbissdbx-dev-1"

DATASET_ID = "ai_wireframe_dataset"

TABLE_ID = "sales_data"

SPEC_FILE = "dashboard_spec.json"


# =========================================================
# BIGQUERY CLIENT
# =========================================================

client = bigquery.Client(
    project=PROJECT_ID
)


# =========================================================
# LOAD THE FULL DATASET
# =========================================================

table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

query = f"""
SELECT *
FROM `{table_ref}`
"""

print("========================================================")
print("LOADING FULL DATASET FROM BIGQUERY")
print("========================================================")

df = client.query(query).to_dataframe()


print("\nDATASET LOADED SUCCESSFULLY")

print(f"\nRows: {len(df)}")
print(f"Columns: {len(df.columns)}")

print("\nColumns:")

for column in df.columns:
    print(f"- {column}")


# =========================================================
# DISPLAY SAMPLE DATA
# =========================================================

print("\n========================================================")
print("SAMPLE DATA")
print("========================================================\n")

print(df.head())


# =========================================================
# LOAD DASHBOARD SPECIFICATION
# =========================================================

print("\n========================================================")
print("LOADING DASHBOARD SPECIFICATION")
print("========================================================")

with open(SPEC_FILE, "r") as file:
    dashboard_spec = json.load(file)


print("\nDASHBOARD SPECIFICATION LOADED SUCCESSFULLY\n")


# =========================================================
# DISPLAY DASHBOARD SPECIFICATION
# =========================================================

print(json.dumps(
    dashboard_spec,
    indent=4
))


# =========================================================
# RENDERER INPUT SUMMARY
# =========================================================

print("\n========================================================")
print("DASHBOARD RENDERER READY")
print("========================================================")

print(f"\nDashboard Title: {dashboard_spec['title']}")

print("\nKPIs to create:")

for kpi in dashboard_spec["kpis"]:
    print(
        f"- {kpi['title']} "
        f"({kpi['aggregation']} of {kpi['field']})"
    )


print("\nCharts to create:")

for chart in dashboard_spec["charts"]:
    print(
        f"- {chart['title']}"
    )

    print(
        f"  Type: {chart['type']}"
    )

    print(
        f"  X-axis: {chart['x_axis']}"
    )

    print(
        f"  Y-axis: {chart['y_axis']}"
    )


print("\nFilters available:")

for filter_name in dashboard_spec["filters"]:
    print(f"- {filter_name}")


print("\n========================================================")
print("READY FOR DASHBOARD RENDERING")
print("========================================================")
