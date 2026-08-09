from google.cloud import bigquery
import json
import re


PROJECT_ID = "vf-grp-gbissdbx-dev-1"
DATASET_ID = "ai_wireframe_dataset"
TABLE_ID = "sales_data"


NUMERIC_TYPES = {
    "INTEGER",
    "INT64",
    "FLOAT",
    "FLOAT64",
    "NUMERIC",
    "BIGNUMERIC",
}


TIME_TYPES = {
    "DATE",
    "DATETIME",
    "TIMESTAMP",
    "TIME",
}


def classify_column(field):
    """
    First-pass heuristic classification.
    The LLM will later refine this classification.
    """

    name = field.name.lower()
    field_type = field.field_type.upper()

    # Time fields
    if field_type in TIME_TYPES:
        return "time_dimension"

    # Numeric fields
    if field_type in NUMERIC_TYPES:

        # Numeric IDs/codes should not normally be treated as measures
        identifier_keywords = [
            "id",
            "code",
            "key"
        ]

        if any(keyword in name for keyword in identifier_keywords):
            return "identifier"

        return "measure"

    # Text fields
    if field_type == "STRING":

        if (
            name.endswith("_id")
            or name.endswith("id")
            or name.endswith("_code")
            or name.endswith("code")
        ):
            return "identifier"

        return "dimension"

    # Boolean fields
    if field_type == "BOOL":
        return "dimension"

    return "unknown"


def create_candidate_kpis(measures):
    """
    Create simple candidate KPI definitions from numeric measures.

    These are candidates, NOT confirmed business KPIs.
    """

    candidate_kpis = []

    for measure in measures:

        # Convert field name to a readable KPI name
        readable_name = measure.replace("_", " ").strip()

        # Capitalize words
        readable_name = readable_name.title()

        candidate_kpis.append(
            {
                "name": f"Total {readable_name}",
                "source": measure,
                "calculation": f"SUM({measure})",
                "type": "aggregation",
                "confidence": "high"
            }
        )

    return candidate_kpis


def detect_possible_derived_metrics(columns):
    """
    Look for obvious relationships between existing numeric fields.

    These are only candidates. We do NOT automatically treat
    them as confirmed business calculations.
    """

    column_names = {
        column["name"].lower(): column["name"]
        for column in columns
    }

    candidates = []

    # Revenue - Cost → Gross Margin
    if "revenue" in column_names and "cost" in column_names:

        revenue = column_names["revenue"]
        cost = column_names["cost"]

        candidates.append(
            {
                "name": "Gross Margin",
                "formula": f"{revenue} - {cost}",
                "source_fields": [
                    revenue,
                    cost
                ],
                "type": "derived_metric_candidate",
                "confidence": "medium",
                "note": (
                    "Candidate only. Business confirmation is required "
                    "before treating this as an official KPI."
                )
            }
        )

    # Gross Margin / Revenue → Margin %
    if (
        "revenue" in column_names
        and "gross_margin" in column_names
    ):

        revenue = column_names["revenue"]
        gross_margin = column_names["gross_margin"]

        candidates.append(
            {
                "name": "Gross Margin %",
                "formula": f"{gross_margin} / {revenue} * 100",
                "source_fields": [
                    gross_margin,
                    revenue
                ],
                "type": "derived_metric_candidate",
                "confidence": "medium",
                "note": (
                    "Candidate only. Division-by-zero and business "
                    "definition must be validated."
                )
            }
        )

    return candidates


def get_null_statistics(client, table_ref, schema):

    null_expressions = []

    for field in schema:

        # BigQuery field names are escaped with backticks
        expression = (
            f"COUNTIF(`{field.name}` IS NULL) "
            f"AS `{field.name}_nulls`"
        )

        null_expressions.append(expression)

    query = f"""
        SELECT
            COUNT(*) AS total_rows,
            {", ".join(null_expressions)}
        FROM `{table_ref}`
    """

    result = client.query(query).result()
    row = next(result)

    null_values = {}

    for field in schema:

        null_values[field.name] = getattr(
            row,
            f"{field.name}_nulls"
        )

    return {
        "total_rows": row.total_rows,
        "null_values": null_values
    }


def get_numeric_statistics(
    client,
    table_ref,
    numeric_fields
):
    """
    Calculate basic statistics for numeric measures.
    """

    if not numeric_fields:
        return {}

    expressions = []

    for field in numeric_fields:

        expressions.extend(
            [
                f"MIN(`{field}`) AS `{field}_min`",
                f"MAX(`{field}`) AS `{field}_max`",
                f"AVG(`{field}`) AS `{field}_avg`"
            ]
        )

    query = f"""
        SELECT
            {", ".join(expressions)}
        FROM `{table_ref}`
    """

    result = client.query(query).result()
    row = next(result)

    statistics = {}

    for field in numeric_fields:

        statistics[field] = {
            "min": getattr(row, f"{field}_min"),
            "max": getattr(row, f"{field}_max"),
            "average": (
                float(getattr(row, f"{field}_avg"))
                if getattr(row, f"{field}_avg") is not None
                else None
            )
        }

    return statistics


def get_time_statistics(
    client,
    table_ref,
    time_fields
):
    """
    Determine minimum and maximum values for time fields.
    """

    if not time_fields:
        return {}

    statistics = {}

    for field in time_fields:

        query = f"""
            SELECT
                MIN(`{field}`) AS min_value,
                MAX(`{field}`) AS max_value
            FROM `{table_ref}`
        """

        result = client.query(query).result()
        row = next(result)

        statistics[field] = {
            "min": str(row.min_value)
            if row.min_value is not None
            else None,

            "max": str(row.max_value)
            if row.max_value is not None
            else None
        }

    return statistics


def profile_table():

    client = bigquery.Client(
        project=PROJECT_ID
    )

    table_ref = (
        f"{PROJECT_ID}."
        f"{DATASET_ID}."
        f"{TABLE_ID}"
    )

    # ---------------------------------------------------------
    # 1. Get BigQuery table metadata
    # ---------------------------------------------------------

    table = client.get_table(table_ref)

    # ---------------------------------------------------------
    # 2. Classify columns
    # ---------------------------------------------------------

    columns = []

    dimensions = []
    measures = []
    time_dimensions = []
    identifiers = []
    unknown = []

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

        else:
            unknown.append(field.name)

    # ---------------------------------------------------------
    # 3. Data quality
    # ---------------------------------------------------------

    quality = get_null_statistics(
        client,
        table_ref,
        table.schema
    )

    # ---------------------------------------------------------
    # 4. Numeric statistics
    # ---------------------------------------------------------

    numeric_statistics = get_numeric_statistics(
        client,
        table_ref,
        measures
    )

    # ---------------------------------------------------------
    # 5. Time statistics
    # ---------------------------------------------------------

    time_statistics = get_time_statistics(
        client,
        table_ref,
        time_dimensions
    )

    # ---------------------------------------------------------
    # 6. Candidate KPIs
    # ---------------------------------------------------------

    candidate_kpis = create_candidate_kpis(
        measures
    )

    # ---------------------------------------------------------
    # 7. Possible derived metrics
    # ---------------------------------------------------------

    derived_metrics = detect_possible_derived_metrics(
        columns
    )

    # ---------------------------------------------------------
    # 8. Final structured profile
    # ---------------------------------------------------------

    profile = {

        "dataset": {
            "project": PROJECT_ID,
            "dataset": DATASET_ID,
            "table": TABLE_ID,
            "full_table_name": table_ref,
            "row_count": table.num_rows
        },

        "columns": columns,

        "semantic_structure": {

            "time_dimensions": time_dimensions,

            "dimensions": dimensions,

            "measures": measures,

            "identifiers": identifiers,

            "unknown": unknown
        },

        "data_quality": {

            "row_count": quality["total_rows"],

            "null_values": quality["null_values"]
        },

        "statistics": {

            "numeric": numeric_statistics,

            "time": time_statistics
        },

        "candidate_kpis": candidate_kpis,

        "candidate_derived_metrics": derived_metrics
    }

    return profile


if __name__ == "__main__":

    profile = profile_table()

    print(
        json.dumps(
            profile,
            indent=2,
            default=str
        )
    )
