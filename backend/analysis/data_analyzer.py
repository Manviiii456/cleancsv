import pandas as pd


def analyze_csv(file_path):
    try:
        # Read CSV file
        df = pd.read_csv(file_path)

        # Basic analysis
        analysis = {
            "total_rows": int(df.shape[0]),
            "total_columns": int(df.shape[1]),
            "column_names": list(df.columns),
            "data_types": df.dtypes.astype(str).to_dict(),
            "statistics": df.describe(include="all").fillna("").to_dict()
        }

        return analysis

    except Exception as e:
        return {"error": str(e)}