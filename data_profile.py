from google.cloud import bigquery
import json
from datetime import date, datetime
from decimal import Decimal


# =========================================================
# CONFIGURATION
# =========================================================

PROJECT_ID = "vf-grp-gbissdbx-dev-1"
DATASET_ID = "ai_wireframe_dataset"
TABLE_ID = "sales_data"

OUTPUT_FILE = "data_profile.json"


# =========================================================
# BIGQUERY CLIENT
# =========================================================

client = bigquery.Client(
    project=PROJECT_ID
)

table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"


# =========================================================
# LOAD TABLE DATA
# =========================================================

query = f"""
SELECT *
FROM `{table_ref}`
"""

df = client.query(query).to_dataframe()


# =========================================================
# JSON SERIALIZATION HELPER
# =========================================================

def json_safe(value):

    # Python date / datetime
    if isinstance(value, (date, datetime)):
        return value.isoformat()

    # Decimal values from BigQuery
    if isinstance(value, Decimal):
        return float(value)

    # NumPy / pandas numeric types
    if hasattr(value, "item"):
        return value.item()

    return value


# =========================================================
# GET BIGQUERY TABLE SCHEMA
# =========================================================

table = client.get_table(table_ref)


# =========================================================
# CLASSIFY COLUMNS
# =========================================================

dimensions = []
measures = []
date_dimensions = []

for field in table.schema:

    field_type = field.field_type.upper()

    # Dimensions
    if field_type in [
        "STRING",
        "DATE",
        "DATETIME",
        "TIMESTAMP"
    ]:
        dimensions.append(field.name)

    # Measures
    if field_type in [
        "INTEGER",
        "INT64",
        "FLOAT",
        "FLOAT64",
        "NUMERIC",
        "BIGNUMERIC"
    ]:
        measures.append(field.name)

    # Date dimensions
    if field_type in [
        "DATE",
        "DATETIME",
        "TIMESTAMP"
    ]:
        date_dimensions.append(field.name)


# =========================================================
# COLUMN-LEVEL PROFILE
# =========================================================

columns = {}

for field in table.schema:

    column_name = field.name
    series = df[column_name]

    column_profile = {

        "name": column_name,

        "type": field.field_type,

        "mode": field.mode,

        "description": field.description,

        "null_count": int(
            series.isna().sum()
        ),

        "distinct_count": int(
            series.nunique(dropna=True)
        )
    }

    # -----------------------------------------------------
    # Numeric statistics
    # -----------------------------------------------------

    if field.field_type.upper() in [
        "INTEGER",
        "INT64",
        "FLOAT",
        "FLOAT64",
        "NUMERIC",
        "BIGNUMERIC"
    ]:

        column_profile["statistics"] = {

            "min": json_safe(
                series.min()
            ),

            "max": json_safe(
                series.max()
            ),

            "mean": json_safe(
                series.mean()
            ),

            "sum": json_safe(
                series.sum()
            )
        }

    # -----------------------------------------------------
    # Categorical information
    # -----------------------------------------------------

    if field.field_type.upper() == "STRING":

        values = (
            series
            .dropna()
            .astype(str)
            .value_counts()
            .head(10)
            .to_dict()
        )

        column_profile["top_values"] = {

            str(key): json_safe(value)

            for key, value in values.items()
        }

    # -----------------------------------------------------
    # Date information
    # -----------------------------------------------------

    if field.field_type.upper() in [
        "DATE",
        "DATETIME",
        "TIMESTAMP"
    ]:

        non_null = series.dropna()

        if len(non_null) > 0:

            column_profile["date_range"] = {

                "min": json_safe(
                    non_null.min()
                ),

                "max": json_safe(
                    non_null.max()
                )
            }

    columns[column_name] = column_profile


# =========================================================
# SAMPLE ROWS
# =========================================================

sample_rows = df.head(10).to_dict(
    orient="records"
)

sample_rows = [

    {
        key: json_safe(value)

        for key, value in row.items()
    }

    for row in sample_rows
]


# =========================================================
# FINAL STRUCTURED PROFILE
# =========================================================

profile = {

    "dataset": {

        "project": PROJECT_ID,

        "dataset": DATASET_ID,

        "table": TABLE_ID,

        "table_reference": table_ref
    },

    "summary": {

        "row_count": int(
            len(df)
        ),

        "column_count": int(
            len(df.columns)
        )
    },

    "dimensions": dimensions,

    "date_dimensions": date_dimensions,

    "measures": measures,

    "columns": columns,

    "sample_rows": sample_rows
}


# =========================================================
# SAVE STRUCTURED JSON
# =========================================================

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        profile,
        file,
        indent=2,
        ensure_ascii=False,
        default=json_safe
    )


# =========================================================
# TERMINAL OUTPUT
# =========================================================

print("=" * 60)
print("DATA PROFILE GENERATED SUCCESSFULLY")
print("=" * 60)

print(
    f"Project: {PROJECT_ID}"
)

print(
    f"Dataset: {DATASET_ID}"
)

print(
    f"Table: {TABLE_ID}"
)

print(
    f"Rows: {len(df)}"
)

print(
    f"Columns: {len(df.columns)}"
)

print("\nDimensions:")

for item in dimensions:
    print(f"  - {item}")

print("\nDate dimensions:")

for item in date_dimensions:
    print(f"  - {item}")

print("\nMeasures:")

for item in measures:
    print(f"  - {item}")

print(
    f"\nStructured JSON saved to: {OUTPUT_FILE}"
)

print("=" * 60)
