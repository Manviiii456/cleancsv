import pandas as pd

def clean_text_format(df, case="none", columns=None):
    cleaned_df = df.copy()
    
    if case not in ["none", "lower", "upper", "title"]:
        raise ValueError("Invalid formatting option")

    if columns is None:
        columns = cleaned_df.select_dtypes(include=["object", "string"]).columns

    changes = {}

    for col in columns:
        if col not in cleaned_df.columns:
            raise ValueError(f"Column '{col}' not found")

        if not (pd.api.types.is_object_dtype(cleaned_df[col]) or
                pd.api.types.is_string_dtype(cleaned_df[col])):
            raise ValueError(f"Column '{col}' is not text")

        original = cleaned_df[col].copy()
        cleaned = original.str.strip()

        if case == "lower":
            cleaned = cleaned.str.lower()
        elif case == "upper":
            cleaned = cleaned.str.upper()
        elif case == "title":
            cleaned = cleaned.str.title()

        changes[col] = int((original != cleaned).sum())
        cleaned_df[col] = cleaned

    return cleaned_df, changes
