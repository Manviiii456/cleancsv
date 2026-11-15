import pandas as pd


def detect_missing_values(df):

    # Count missing values in each column
    missing_counts = df.isnull().sum()

    # Calculate missing percentage
    missing_percentage = (missing_counts / len(df)) * 100 if len(df) > 0 else missing_counts

    # Prepare result
    result = {
        "total_missing_values": int(missing_counts.sum()),
        "missing_details": {}
    }

    for column in df.columns:
        result["missing_details"][column] = {
            "missing_count": int(missing_counts[column]),
            "missing_percentage": round(float(missing_percentage[column]), 2)
        }

    return result