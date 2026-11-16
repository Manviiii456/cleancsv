import pandas as pd

def fill_missing_values(df, method="mean", columns=None):
    cleaned_df = df.copy()

    if method not in ["mean", "median"]:
        raise ValueError("Method must be mean or median")

    if columns is None:
        columns = cleaned_df.select_dtypes(include="number").columns

    filled_counts = {}

    for col in columns:
        if col not in cleaned_df.columns:
            raise ValueError(f"Column '{col}' not found")

        if not pd.api.types.is_numeric_dtype(cleaned_df[col]):
            raise ValueError(f"Column '{col}' is not numeric")

        missing = cleaned_df[col].isna().sum()

        if missing == 0:
            continue

        value = cleaned_df[col].mean() if method == "mean" else cleaned_df[col].median()

        if pd.notna(value):
            cleaned_df[col] = cleaned_df[col].fillna(value)
            filled_counts[col] = missing

    return cleaned_df, filled_counts
