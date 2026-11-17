import pandas as pd


def detect_outliers(df):

    outliers = {}

    # Check numerical columns
    for column in df.select_dtypes(include="number").columns:

        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)

        IQR = Q3 - Q1

        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        # Find outliers
        values = df[
            (df[column] < lower) |
            (df[column] > upper)
        ]

        outliers[column] = len(values)

    return outliers