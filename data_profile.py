from google.cloud import bigquery
import json


PROJECT_ID = "vf-grp-gbissdbx-dev-1"
DATASET_ID = "ai_wireframe_dataset"
TABLE_ID = "sales_data"


def classify_column(field):
    """
    Classify a BigQuery column based on its data type.
    This is a first-pass heuristic. Later, the LLM can
    refine the semantic classification.
    """

    name = field.name.lower()
    field_type = field.field_type

    # Time-related columns
    if field_type in ["DATE", "DATETIME", "TIMESTAMP", "TIME"]:
        return "time_dimension"

    # Numeric columns
    if field_type in ["INTEGER", "INT64", "FLOAT", "FLOAT64", "NUMERIC", "BIGNUMERIC"]:
        # Some numeric fields are likely identifiers rather than measures
        identifier_keywords = [
            "id",
            "code",
            "key"
        ]

        if any(keyword in name for keyword in identifier_keywords):
            return "identifier"

        return "measure"

    # Text / categorical fields
    if field_type in ["STRING"]:
        # Detect likely identifiers
        if name.endswith("_id") or name.endswith("id"):
            return "identifier"

        return "dimension"

    # Boolean fields
    if field_type == "BOOL":
        return "dimension"

    return "unknown"


def profile_table():

    client = bigquery.Client(project=PROJECT_ID)

    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

    # Get table metadata
    table = client.get_table(table_ref)

    dimensions = []
    measures = []
    time_dimensions = []
    identifiers = []
    columns = []

    # Classify every column
    for field in table.schema:

        role = classify_column(field)

        column_info = {
            "name": field.name,
            "type": field.field_type,
            "mode": field.mode,
            "role": role
        }

        columns.append(column_info)

        if role == "dimension":
            dimensions.append(field.name)

        elif role == "measure":
            measures.append(field.name)

        elif role == "time_dimension":
            time_dimensions.append(field.name)

        elif role == "identifier":
            identifiers.append(field.name)

    # Build dynamic SQL for basic data-quality information
    null_expressions = []

    for field in table.schema:
        null_expressions.append(
            f"COUNTIF(`{field.name}` IS NULL) AS `{field.name}_nulls`"
        )

    null_query = f"""
        SELECT
            COUNT(*) AS total_rows,
            {", ".join(null_expressions)}
        FROM `{table_ref}`
    """

    result = client.query(null_query).result()
    row = next(result)

    null_values = {}

    for field in table.schema:
        null_values[field.name] = getattr(
            row,
            f"{field.name}_nulls"
        )

    # Build final profile
    profile = {
        "table": table_ref,
        "row_count": table.num_rows,

        "columns": columns,

        "semantic_structure": {
            "time_dimensions": time_dimensions,
            "dimensions": dimensions,
            "measures": measures,
            "identifiers": identifiers
        },

        "data_quality": {
            "null_values": null_values
        }
    }

    return profile


if __name__ == "__main__":

    profile = profile_table()

    print(
        json.dumps(
            profile,
            indent=2
        )
    )
