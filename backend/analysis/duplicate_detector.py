import pandas as pd


def detect_duplicates(df):

    # Find duplicate rows
    duplicate_rows = df[df.duplicated()]

    # Count duplicates
    total_duplicates = int(df.duplicated().sum())

    # Get duplicate row indexes
    duplicate_indexes = duplicate_rows.index.tolist()

    result = {
        "total_duplicates": total_duplicates,
        "duplicate_indexes": duplicate_indexes,
        "duplicate_records": duplicate_rows.to_dict(orient="records")
    }

    return result