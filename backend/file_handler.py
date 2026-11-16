
import pandas as pd
from io import BytesIO
from pathlib import Path

# Project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Upload directory
UPLOAD_DIR = BASE_DIR / "storage" / "uploads"

# Create upload directory if it does not exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def read_csv_file(file_content):

    try:
        # Read CSV using Pandas
        df = pd.read_csv(
            BytesIO(file_content),
            encoding="utf-8-sig"
        )

        # Check whether CSV has columns
        if len(df.columns) == 0:
            raise ValueError("CSV contains no columns")

        # Check whether CSV has records
        if df.empty:
            raise ValueError("CSV file contains no records")

        # Check for empty column names
        if any(str(col).strip() == "" for col in df.columns):
            raise ValueError("CSV contains empty column names")

        # Return the DataFrame
        return df

    except pd.errors.EmptyDataError:
        raise ValueError("CSV file is empty")

    except pd.errors.ParserError:
        raise ValueError("Invalid CSV format")

    except UnicodeDecodeError:
        raise ValueError("CSV encoding is not supported")

    except pd.errors.OutOfBoundsDatetime:
        raise ValueError("CSV contains invalid date values")


def save_uploaded_file(file_id, content):

    # Generate file path
    file_path = UPLOAD_DIR / f"{file_id}.csv"

    # Save original CSV
    file_path.write_bytes(content)

    return file_path


def get_uploaded_file(file_id):

    # Locate uploaded CSV
    file_path = UPLOAD_DIR / f"{file_id}.csv"

    if not file_path.exists():
        raise FileNotFoundError("Uploaded CSV file not found")

    return file_path
