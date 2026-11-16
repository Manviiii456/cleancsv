import pandas as pd

def count_duplicates(df):
    return df.duplicated().sum()


def remove_duplicates(df):
    cleaned_df = df.drop_duplicates().copy()
    removed = len(df) - len(cleaned_df)

    return cleaned_df, removed
