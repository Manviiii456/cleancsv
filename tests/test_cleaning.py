import pandas as pd

from backend.cleaning.duplicate_remover import count_duplicates, remove_duplicates
from backend.cleaning.format_cleaner import clean_text_format
from backend.cleaning.missing_handler import fill_missing_values


def test_count_duplicates():
    df = pd.DataFrame({"Name": ["A", "B", "B"]})

    result = count_duplicates(df)

    assert result == 1


def test_remove_duplicates():
    df = pd.DataFrame({"Name": ["A", "B", "B"]})

    result, removed = remove_duplicates(df)

    assert removed == 1
    assert result.duplicated().sum() == 0


def test_clean_text_format():
    df = pd.DataFrame({"Name": ["  MANVITH  ", "  SAM  "]})

    result, changes = clean_text_format(df, case="lower")

    assert result["Name"].iloc[0] == "manvith"
    assert result["Name"].iloc[1] == "sam"


def test_fill_missing_values():
    df = pd.DataFrame({"Age": [10, None, 30]})

    result, filled = fill_missing_values(df, method="mean")

    assert result["Age"].isnull().sum() == 0
    assert result["Age"].iloc[1] == 20