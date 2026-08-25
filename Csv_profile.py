import pandas as pd


def profile_csv_dataframe(df: pd.DataFrame):

    profile = {
        "total_rows": int(len(df)),
        "total_columns": int(len(df.columns)),
        "dimensions": [],
        "date_dimensions": [],
        "measures": [],
        "columns": []
    }

    for column in df.columns:

        column_data = df[column]

        column_info = {
            "name": column,
            "data_type": str(column_data.dtype),
            "missing_values": int(column_data.isnull().sum()),
            "unique_values": int(column_data.nunique())
        }


        # ==========================================
        # 1. NUMERIC COLUMN → MEASURE
        # ==========================================

        if pd.api.types.is_numeric_dtype(column_data):

            column_info["column_type"] = "numeric"

            statistics = {
                "min": (
                    float(column_data.min())
                    if pd.notnull(column_data.min())
                    else None
                ),

                "max": (
                    float(column_data.max())
                    if pd.notnull(column_data.max())
                    else None
                ),

                "mean": (
                    float(column_data.mean())
                    if pd.notnull(column_data.mean())
                    else None
                ),

                "sum": (
                    float(column_data.sum())
                    if pd.notnull(column_data.sum())
                    else None
                )
            }

            column_info["statistics"] = statistics

            profile["measures"].append(column)


        # ==========================================
        # 2. TRY TO DETECT DATE COLUMN
        # ==========================================

        elif (
            "date" in column.lower()
            or "time" in column.lower()
            or "year" in column.lower()
            or "month" in column.lower()
        ):

            column_info["column_type"] = "date"

            profile["date_dimensions"].append(column)


        # ==========================================
        # 3. EVERYTHING ELSE → DIMENSION
        # ==========================================

        else:

            column_info["column_type"] = "categorical"

            sample_values = (
                column_data
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            column_info["sample_values"] = sample_values[:10]

            profile["dimensions"].append(column)


        # Add complete column information
        profile["columns"].append(column_info)


    return profile
