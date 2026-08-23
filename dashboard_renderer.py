import json
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.gridspec import GridSpec
from google.cloud import bigquery


# =========================================================
# CONFIGURATION
# =========================================================

PROJECT_ID = "vf-grp-gbissdbx-dev-1"

DATASET_ID = "ai_wireframe_dataset"

TABLE_ID = "sales_data"

SPEC_FILE = "dashboard_spec.json"

DASHBOARD_OUTPUT = "dashboard.png"


# =========================================================
# BIGQUERY CLIENT
# =========================================================

client = bigquery.Client(
    project=PROJECT_ID
)


# =========================================================
# LOAD FULL DATASET
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

print(
    json.dumps(
        dashboard_spec,
        indent=4
    )
)


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

    print(f"- {chart['title']}")

    print(f"  Type: {chart['type']}")

    print(f"  X-axis: {chart['x_axis']}")

    print(f"  Y-axis: {chart['y_axis']}")


print("\nFilters available:")

for filter_name in dashboard_spec["filters"]:

    print(f"- {filter_name}")


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


    # -----------------------------------------------------
    # PERFORM AGGREGATION DYNAMICALLY
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # STORE KPI RESULT
    # -----------------------------------------------------

    kpi_result = {

        "title": kpi_title,

        "field": field,

        "aggregation": aggregation,

        "value": float(value) if value is not None else None

    }


    kpi_results.append(kpi_result)


    # -----------------------------------------------------
    # PRINT KPI RESULT
    # -----------------------------------------------------

    print(f"{kpi_title}: {value}")


# =========================================================
# FINAL KPI RESULTS
# =========================================================

print("\n========================================================")
print("KPI CALCULATION COMPLETE")
print("========================================================\n")

print(
    json.dumps(
        kpi_results,
        indent=4
    )
)


# =========================================================
# GENERATE INDIVIDUAL CHARTS
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


    # -----------------------------------------------------
    # GROUP DATA
    # -----------------------------------------------------

    chart_data = (
        df.groupby(x_axis)[y_axis]
        .sum()
        .reset_index()
    )


    # -----------------------------------------------------
    # CREATE INDIVIDUAL CHART
    # -----------------------------------------------------

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

        print(
            f"Unsupported chart type: {chart_type}"
        )

        continue


    # -----------------------------------------------------
    # CHART FORMATTING
    # -----------------------------------------------------

    plt.title(chart_title)

    plt.xlabel(x_axis)

    plt.ylabel(y_axis)

    plt.xticks(rotation=45)

    plt.tight_layout()


    # -----------------------------------------------------
    # SAVE INDIVIDUAL CHART
    # -----------------------------------------------------

    filename = f"chart_{index + 1}.png"

    plt.savefig(filename)

    plt.close()


    print(f"Saved: {filename}")


print("\n========================================================")
print("CHART GENERATION COMPLETE")
print("========================================================")


# =========================================================
# CREATE COMPLETE DASHBOARD
# =========================================================

print("\n========================================================")
print("CREATING COMPLETE DASHBOARD")
print("========================================================")


# ---------------------------------------------------------
# CREATE DASHBOARD CANVAS
# ---------------------------------------------------------

fig = plt.figure(
    figsize=(18, 12)
)


# ---------------------------------------------------------
# CREATE LAYOUT GRID
# ---------------------------------------------------------

grid = GridSpec(
    4,
    4,
    figure=fig,
    height_ratios=[
        0.6,
        1,
        3,
        3
    ]
)


# =========================================================
# DASHBOARD TITLE
# =========================================================

title_ax = fig.add_subplot(
    grid[0, :]
)

title_ax.axis("off")


title_ax.text(
    0.5,
    0.5,
    dashboard_spec["title"],
    ha="center",
    va="center",
    fontsize=24,
    fontweight="bold"
)


# =========================================================
# KPI CARDS
# =========================================================

for index, kpi in enumerate(kpi_results):

    # Maximum 4 KPI cards
    if index >= 4:

        break


    ax = fig.add_subplot(
        grid[1, index]
    )


    ax.axis("off")


    # -----------------------------------------------------
    # KPI TITLE
    # -----------------------------------------------------

    ax.text(
        0.5,
        0.65,
        kpi["title"],
        ha="center",
        va="center",
        fontsize=12,
        fontweight="bold"
    )


    # -----------------------------------------------------
    # KPI VALUE
    # -----------------------------------------------------

    ax.text(
        0.5,
        0.35,
        f"{kpi['value']:,.0f}",
        ha="center",
        va="center",
        fontsize=20
    )


    # -----------------------------------------------------
    # KPI CARD BORDER
    # -----------------------------------------------------

    for spine in ax.spines.values():

        spine.set_visible(True)


# =========================================================
# CREATE CHARTS INSIDE DASHBOARD
# =========================================================

for index, chart in enumerate(dashboard_spec["charts"]):

    chart_title = chart["title"]

    chart_type = chart["type"]

    x_axis = chart["x_axis"]

    y_axis = chart["y_axis"]


    # -----------------------------------------------------
    # GROUP DATA
    # -----------------------------------------------------

    chart_data = (
        df.groupby(x_axis)[y_axis]
        .sum()
        .reset_index()
    )


    # -----------------------------------------------------
    # DECIDE CHART POSITION
    # -----------------------------------------------------

    if index == 0:

        # Primary chart takes full width

        ax = fig.add_subplot(
            grid[2, :]
        )


    elif index == 1:

        # Second chart on left

        ax = fig.add_subplot(
            grid[3, :2]
        )


    elif index == 2:

        # Third chart on right

        ax = fig.add_subplot(
            grid[3, 2:]
        )


    else:

        print(
            f"Skipping extra chart: {chart_title}"
        )

        continue


    # -----------------------------------------------------
    # DRAW CHART
    # -----------------------------------------------------

    if chart_type == "line":

        ax.plot(
            chart_data[x_axis],
            chart_data[y_axis],
            marker="o"
        )


    elif chart_type == "bar":

        ax.bar(
            chart_data[x_axis].astype(str),
            chart_data[y_axis]
        )


    else:

        print(
            f"Unsupported chart type: {chart_type}"
        )

        continue


    # -----------------------------------------------------
    # CHART FORMATTING
    # -----------------------------------------------------

    ax.set_title(
        chart_title,
        fontsize=14,
        fontweight="bold"
    )


    ax.set_xlabel(
        x_axis
    )


    ax.set_ylabel(
        y_axis
    )


    ax.tick_params(
        axis="x",
        rotation=45
    )


# =========================================================
# FINAL LAYOUT
# =========================================================

plt.tight_layout()


# =========================================================
# SAVE COMPLETE DASHBOARD
# =========================================================

plt.savefig(
    DASHBOARD_OUTPUT,
    dpi=150,
    bbox_inches="tight"
)

plt.close()


print("\n========================================================")
print("DASHBOARD GENERATED SUCCESSFULLY")
print("========================================================")

print(f"\nSaved as: {DASHBOARD_OUTPUT}")
