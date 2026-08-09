from google.cloud import bigquery


PROJECT_ID = "vf-grp-gbissdbx-dev-1"
DATASET_ID = "ai_wireframe_dataset"
TABLE_ID = "sales_data"


def get_table_schema():
    client = bigquery.Client(project=PROJECT_ID)

    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    table = client.get_table(table_ref)

    print(f"Table: {table_ref}")
    print(f"Rows: {table.num_rows}")
    print("\nColumns:")

    for field in table.schema:
        print(f"- {field.name}: {field.field_type}")


if __name__ == "__main__":
    get_table_schema()
