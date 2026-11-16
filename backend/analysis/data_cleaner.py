import pandas as pd

def clean_data(df):

    # Remove duplicate rows
    df = df.drop_duplicates()

    # Fill missing numerical values
    for column in df.select_dtypes(include='number').columns:
        df[column] = df[column].fillna(df[column].median())

    # Fill missing text values
    for column in df.select_dtypes(include='object').columns:
        df[column] = df[column].fillna(
            df[column].mode()[0] if not df[column].mode().empty else "Unknown"
        )

    return df