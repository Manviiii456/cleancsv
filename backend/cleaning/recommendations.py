import pandas as pd

def generate_recommendations(df):
    recommendations = []

    duplicates = df.duplicated().sum()
    if duplicates > 0:
        recommendations.append({
            "issue": "Duplicate Rows",
            "count": int(duplicates),
            "suggestion": "Remove duplicate rows"
        })

    missing = df.isnull().sum()
    for col, count in missing.items():
        if count > 0:
            suggestion = "Fill using mean or median" if pd.api.types.is_numeric_dtype(df[col]) else "Review missing values"
            recommendations.append({
                "issue": f"Missing Values in {col}",
                "count": int(count),
                "suggestion": suggestion
            })

    for col in df.select_dtypes(include=["object", "string"]).columns:
        spaces = df[col].apply(
            lambda x: isinstance(x, str) and x != x.strip()
        ).sum()

        if spaces > 0:
            recommendations.append({
                "issue": f"Extra Spaces in {col}",
                "count": int(spaces),
                "suggestion": "Trim extra spaces"
            })

    if not recommendations:
        recommendations.append({
            "issue": "No Issues Found",
            "count": 0,
            "suggestion": "Data is ready for use"
        })

    return recommendations
