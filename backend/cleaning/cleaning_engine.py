import pandas as pd

from .duplicate_remover import remove_duplicates
from .missing_handler import fill_missing_values
from .format_cleaner import clean_text_format


def clean_data(df, remove_dups=True, missing_method=None,
               text_case="none"):

    cleaned_df = df.copy()
    report = {}

    if remove_dups:
        cleaned_df, count = remove_duplicates(cleaned_df)
        report["duplicates_removed"] = count

    if missing_method:
        cleaned_df, count = fill_missing_values(
            cleaned_df, method=missing_method
        )
        report["missing_values_filled"] = count

    cleaned_df, changes = clean_text_format(
        cleaned_df, case=text_case
    )
    report["text_changes"] = changes

    return cleaned_df, report


def save_cleaned_csv(df, output_path):
    df.to_csv(output_path, index=False)
    return output_path
