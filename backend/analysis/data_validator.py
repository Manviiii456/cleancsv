import pandas as pd

def validate_data(df):

    errors = []

    # Check for empty dataset
    if df.empty:
        errors.append("Dataset is empty")

    # Check for duplicate column names
    if df.columns.duplicated().any():
        errors.append("Duplicate column names found")

    # Check for invalid data
    if df.isnull().all().any():
        errors.append("Columns with all missing values found")

    result = {
        "is_valid": len(errors) == 0,
        "errors": errors
    }

    return result