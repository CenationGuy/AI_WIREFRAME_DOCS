from google.cloud import bigquery
import json


PROJECT_ID = "vf-grp-gbissdbx-dev-1"
DATASET_ID = "ai_wireframe_dataset"
TABLE_ID = "sales_data"


def profile_table():
    client = bigquery.Client(project=PROJECT_ID)

    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

    # Get table metadata
    table = client.get_table(table_ref)

    # Collect column information
    columns = []

    for field in table.schema:
        columns.append({
            "name": field.name,
            "type": field.field_type,
            "mode": field.mode
        })

    # Get statistics
    query = f"""
        SELECT
            COUNT(*) AS total_rows,

            COUNTIF(Date IS NULL) AS null_date,
            COUNTIF(Region IS NULL) AS null_region,
            COUNTIF(Product IS NULL) AS null_product,
            COUNTIF(Revenue IS NULL) AS null_revenue,
            COUNTIF(Cost IS NULL) AS null_cost,
            COUNTIF(Units IS NULL) AS null_units,
            COUNTIF(Gross_Margin IS NULL) AS null_gross_margin,

            COUNT(DISTINCT Region) AS unique_regions,
            COUNT(DISTINCT Product) AS unique_products,

            MIN(Date) AS min_date,
            MAX(Date) AS max_date,

            MIN(Revenue) AS min_revenue,
            MAX(Revenue) AS max_revenue,
            AVG(Revenue) AS avg_revenue,

            MIN(Cost) AS min_cost,
            MAX(Cost) AS max_cost,
            AVG(Cost) AS avg_cost,

            MIN(Units) AS min_units,
            MAX(Units) AS max_units,
            AVG(Units) AS avg_units

        FROM `{table_ref}`
    """

    result = client.query(query).result()
    row = next(result)

    # Build structured profile
    profile = {
        "table": table_ref,
        "rows": table.num_rows,

        "columns": columns,

        "statistics": {
            "null_values": {
                "Date": row.null_date,
                "Region": row.null_region,
                "Product": row.null_product,
                "Revenue": row.null_revenue,
                "Cost": row.null_cost,
                "Units": row.null_units,
                "Gross_Margin": row.null_gross_margin
            },

            "unique_values": {
                "regions": row.unique_regions,
                "products": row.unique_products
            },

            "date_range": {
                "min": str(row.min_date),
                "max": str(row.max_date)
            },

            "revenue": {
                "min": row.min_revenue,
                "max": row.max_revenue,
                "average": float(row.avg_revenue)
            },

            "cost": {
                "min": row.min_cost,
                "max": row.max_cost,
                "average": float(row.avg_cost)
            },

            "units": {
                "min": row.min_units,
                "max": row.max_units,
                "average": float(row.avg_units)
            }
        }
    }

    return profile


if __name__ == "__main__":
    profile = profile_table()

    print(json.dumps(profile, indent=2))
