from google.cloud import bigquery


PROJECT_ID = "vf-grp-gbissdbx-dev-1"
DATASET_ID = "ai_wireframe_dataset"
TABLE_ID = "sales_data"


def profile_table():
    client = bigquery.Client(project=PROJECT_ID)

    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

    # Get table metadata
    table = client.get_table(table_ref)

    print("\n==============================")
    print("DATASET PROFILE")
    print("==============================")

    print(f"Table: {table_ref}")
    print(f"Rows: {table.num_rows}")

    print("\nColumns:")

    for field in table.schema:
        print(f"- {field.name}: {field.field_type}")

    # Get column statistics
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

    print("\n==============================")
    print("STATISTICS")
    print("==============================")

    print(f"Total rows: {row.total_rows}")

    print("\nNull values:")
    print(f"Date: {row.null_date}")
    print(f"Region: {row.null_region}")
    print(f"Product: {row.null_product}")
    print(f"Revenue: {row.null_revenue}")
    print(f"Cost: {row.null_cost}")
    print(f"Units: {row.null_units}")
    print(f"Gross Margin: {row.null_gross_margin}")

    print("\nUnique values:")
    print(f"Regions: {row.unique_regions}")
    print(f"Products: {row.unique_products}")

    print("\nDate range:")
    print(f"From: {row.min_date}")
    print(f"To: {row.max_date}")

    print("\nRevenue:")
    print(f"Min: {row.min_revenue}")
    print(f"Max: {row.max_revenue}")
    print(f"Average: {row.avg_revenue:.2f}")

    print("\nCost:")
    print(f"Min: {row.min_cost}")
    print(f"Max: {row.max_cost}")
    print(f"Average: {row.avg_cost:.2f}")

    print("\nUnits:")
    print(f"Min: {row.min_units}")
    print(f"Max: {row.max_units}")
    print(f"Average: {row.avg_units:.2f}")


if __name__ == "__main__":
    profile_table()
