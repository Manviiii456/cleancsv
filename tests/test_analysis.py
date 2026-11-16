import pandas as pd

from backend.analysis.data_analyzer import analyze_csv
from backend.analysis.missing_values import detect_missing_values
from backend.analysis.duplicate_detector import detect_duplicates
from backend.analysis.data_validator import validate_data
from backend.analysis.outlier_detector import detect_outliers
from backend.analysis.data_cleaner import clean_data


def test_analyze_csv(tmp_path):
    file_path = tmp_path / "sample.csv"
    pd.DataFrame({"Name": ["A", "B"], "Age": [20, 25]}).to_csv(
        file_path, index=False
    )

    result = analyze_csv(file_path)

    assert result["total_rows"] == 2
    assert result["total_columns"] == 2


def test_detect_missing_values():
    df = pd.DataFrame({"Age": [20, None, 30]})

    result = detect_missing_values(df)

    assert result["total_missing_values"] == 1


def test_detect_duplicates():
    df = pd.DataFrame({"Name": ["A", "B", "B"]})

    result = detect_duplicates(df)

    assert result["total_duplicates"] == 1


def test_validate_data():
    df = pd.DataFrame({"Age": [20, 25, 30]})

    result = validate_data(df)

    assert result["is_valid"] is True


def test_detect_outliers():
    df = pd.DataFrame({"Marks": [10, 11, 12, 13, 100]})

    result = detect_outliers(df)

    assert result["Marks"] == 1


def test_clean_data():
    df = pd.DataFrame({
        "Name": ["A", "B", "B"],
        "Age": [20, None, 30]
    })

    result = clean_data(df)

    assert result.duplicated().sum() == 0
    assert result["Age"].isnull().sum() == 0