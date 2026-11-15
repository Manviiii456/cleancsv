import pandas as pd

from analysis.data_analyzer import analyze_csv
from analysis.missing_values import detect_missing_values
from analysis.duplicate_detector import detect_duplicates
from analysis.data_validator import validate_data
from analysis.outlier_detector import detect_outliers
from analysis.data_cleaner import clean_data

# Sample dataset
data = {
    "Name": ["A", "B", "B", "D", "E"],
    "Age": [20, 25, 25, None, 100],
    "Marks": [80, 90, 90, 70, 85]
}

df = pd.DataFrame(data)

print("Original Dataset:")
print(df)

print("\nMissing Values:")
print(detect_missing_values(df))

print("\nDuplicate Records:")
print(detect_duplicates(df))

print("\nData Validation:")
print(validate_data(df))

print("\nOutliers:")
print(detect_outliers(df))

print("\nCleaned Dataset:")
print(clean_data(df))