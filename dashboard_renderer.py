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



# =========================================================
# CALCULATE KPIs
# =========================================================

print("\n========================================================")
print("CALCULATING KPIs")
print("========================================================\n")

kpi_results = []

for kpi in dashboard_spec["kpis"]:

    kpi_title = kpi["title"]
    field = kpi["field"]
    aggregation = kpi["aggregation"]

    # ---------------------------------------------
    # Perform aggregation dynamically
    # ---------------------------------------------

    if aggregation == "sum":
        value = df[field].sum()

    elif aggregation == "mean":
        value = df[field].mean()

    elif aggregation == "min":
        value = df[field].min()

    elif aggregation == "max":
        value = df[field].max()

    elif aggregation == "count":
        value = df[field].count()

    else:
        print(
            f"Unsupported aggregation: {aggregation}"
        )
        value = None


    # ---------------------------------------------
    # Store KPI result
    # ---------------------------------------------

    kpi_result = {
        "title": kpi_title,
        "field": field,
        "aggregation": aggregation,
        "value": float(value) if value is not None else None
    }

    kpi_results.append(kpi_result)


    # ---------------------------------------------
    # Print result
    # ---------------------------------------------

    print(f"{kpi_title}: {value}")


# =========================================================
# FINAL KPI RESULTS
# =========================================================

print("\n========================================================")
print("KPI CALCULATION COMPLETE")
print("========================================================\n")

print(json.dumps(
    kpi_results,
    indent=4
))






# =========================================================
# GENERATE CHARTS
# =========================================================

print("\n========================================================")
print("GENERATING CHARTS")
print("========================================================")

for index, chart in enumerate(dashboard_spec["charts"]):

    chart_title = chart["title"]
    chart_type = chart["type"]
    x_axis = chart["x_axis"]
    y_axis = chart["y_axis"]

    print(f"\nCreating: {chart_title}")

    # ---------------------------------------------
    # GROUP DATA
    # ---------------------------------------------

    chart_data = (
        df.groupby(x_axis)[y_axis]
        .sum()
        .reset_index()
    )

    # ---------------------------------------------
    # CREATE CHART
    # ---------------------------------------------

    plt.figure(figsize=(10, 6))

    if chart_type == "line":

        plt.plot(
            chart_data[x_axis],
            chart_data[y_axis],
            marker="o"
        )

    elif chart_type == "bar":

        plt.bar(
            chart_data[x_axis].astype(str),
            chart_data[y_axis]
        )

    else:

        print(f"Unsupported chart type: {chart_type}")
        continue

    # ---------------------------------------------
    # CHART FORMATTING
    # ---------------------------------------------

    plt.title(chart_title)

    plt.xlabel(x_axis)

    plt.ylabel(y_axis)

    plt.xticks(rotation=45)

    plt.tight_layout()

    # ---------------------------------------------
    # SAVE CHART
    # ---------------------------------------------

    filename = f"chart_{index + 1}.png"

    plt.savefig(filename)

    plt.close()

    print(f"Saved: {filename}")


print("\n========================================================")
print("CHART GENERATION COMPLETE")
print("========================================================")
