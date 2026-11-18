
import math
import os
import jwt
import numpy as np

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Depends
)
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pathlib import Path
from uuid import uuid4
from pymongo.errors import PyMongoError

# File handling functions
from backend.file_handler import (
    read_csv_file,
    save_uploaded_file,
    get_uploaded_file
)

# Member 2 - Data analysis
from backend.analysis.data_analyzer import analyze_csv
from backend.analysis.data_validator import validate_data
from backend.analysis.missing_values import detect_missing_values
from backend.analysis.duplicate_detector import detect_duplicates
from backend.analysis.outlier_detector import detect_outliers

# Member 3 - Data cleaning
from backend.cleaning.cleaning_engine import (
    clean_data,
    save_cleaned_csv
)
from backend.cleaning.recommendations import generate_recommendations

# Database functions
from backend.database import (
    add_dataset,
    get_dataset,
    get_history,
    update_cleaned_file
)


router = APIRouter()


# JWT Authentication
security = HTTPBearer()

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "cleancsv-demo-secret-change-before-deployment"
)

ALGORITHM = "HS256"


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        email = payload.get("sub")

        if not email:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token"
            )

        return email

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


BASE_DIR = Path(__file__).resolve().parent.parent
CLEANED_DIR = BASE_DIR / "storage" / "cleaned"
CLEANED_DIR.mkdir(parents=True, exist_ok=True)


# Convert NaN and infinity into JSON-safe values
def clean_for_json(value):

    if isinstance(value, dict):
        return {
            key: clean_for_json(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [clean_for_json(item) for item in value]

    if isinstance(value, np.generic):
        value = value.item()

    if isinstance(value, float):
        if not math.isfinite(value):
            return None

    return value


# 1. Health check (public)
@router.get("/health")
def health_check():
    return {
        "message": "CleanCSV API is working",
        "status": "Healthy"
    }


# 2. Upload CSV (protected)
@router.post("/upload")
async def upload_csv(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user)
):

    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(400, "Only CSV files are allowed")

    content = await file.read()

    if not content:
        raise HTTPException(400, "Uploaded file is empty")

    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(400, "File size must be below 10 MB")

    try:
        df = read_csv_file(content)

        file_id = str(uuid4())

        file_path = save_uploaded_file(file_id, content)

        add_dataset(
            file_id,
            Path(file.filename).name,
            file_path,
            len(df),
            len(df.columns)
        )

        return {
            "message": "CSV uploaded successfully",
            "file_id": file_id,
            "filename": Path(file.filename).name,
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist()
        }

    except ValueError as error:
        raise HTTPException(400, str(error))

    except PyMongoError:
        raise HTTPException(503, "Unable to save file details in MongoDB")


# 3. Dataset details (protected)
@router.get("/dataset/{file_id}")
def dataset_details(
    file_id: str,
    current_user: str = Depends(get_current_user)
):

    try:
        dataset = get_dataset(file_id)

        if not dataset:
            raise HTTPException(404, "Dataset not found")

        return dataset

    except PyMongoError:
        raise HTTPException(503, "Unable to retrieve dataset from MongoDB")


# 4. Upload history (protected)
@router.get("/history")
def upload_history(
    current_user: str = Depends(get_current_user)
):

    try:
        return {"history": get_history()}

    except PyMongoError:
        raise HTTPException(503, "Unable to retrieve upload history")


# 5. Data analysis (protected)
@router.get("/analysis/{file_id}")
def analyze_dataset(
    file_id: str,
    current_user: str = Depends(get_current_user)
):

    try:
        dataset = get_dataset(file_id)

        if not dataset:
            raise HTTPException(404, "Dataset not found")

        file_path = get_uploaded_file(file_id)

        df = read_csv_file(file_path.read_bytes())

        validation = validate_data(df)

        if not validation["is_valid"]:
            raise HTTPException(400, validation["errors"])

        analysis = analyze_csv(str(file_path))

        if "error" in analysis:
            raise HTTPException(400, analysis["error"])

        missing = detect_missing_values(df)
        duplicates = detect_duplicates(df)
        outliers = detect_outliers(df)

        result = {
            "file_id": file_id,
            "filename": dataset["filename"],
            "validation": validation,
            "analysis": analysis,
            "missing_values": missing,
            "duplicates": duplicates,
            "outliers": outliers
        }

        return clean_for_json(result)

    except FileNotFoundError:
        raise HTTPException(404, "Uploaded CSV file not found")

    except PyMongoError:
        raise HTTPException(503, "Database error")


# 6. Cleaning recommendations (protected)
@router.get("/recommendations/{file_id}")
def cleaning_recommendations(
    file_id: str,
    current_user: str = Depends(get_current_user)
):

    try:
        dataset = get_dataset(file_id)

        if not dataset:
            raise HTTPException(404, "Dataset not found")

        file_path = get_uploaded_file(file_id)

        df = read_csv_file(file_path.read_bytes())

        recommendations = generate_recommendations(df)

        return {
            "file_id": file_id,
            "recommendations": recommendations
        }

    except FileNotFoundError:
        raise HTTPException(404, "Uploaded CSV file not found")

    except PyMongoError:
        raise HTTPException(503, "Database error")


# 7. Clean CSV (protected)
@router.post("/clean/{file_id}")
def clean_dataset(
    file_id: str,
    remove_dups: bool = True,
    missing_method: str = None,
    text_case: str = "none",
    current_user: str = Depends(get_current_user)
):

    try:
        dataset = get_dataset(file_id)

        if not dataset:
            raise HTTPException(404, "Dataset not found")

        if missing_method not in [None, "mean", "median"]:
            raise HTTPException(
                400,
                "missing_method must be mean or median"
            )

        if text_case not in ["none", "lower", "upper", "title"]:
            raise HTTPException(400, "Invalid text formatting option")

        file_path = get_uploaded_file(file_id)

        df = read_csv_file(file_path.read_bytes())

        cleaned_df, report = clean_data(
            df,
            remove_dups=remove_dups,
            missing_method=missing_method,
            text_case=text_case
        )

        output_path = CLEANED_DIR / f"{file_id}_cleaned.csv"

        save_cleaned_csv(cleaned_df, output_path)

        update_cleaned_file(file_id, output_path)

        return clean_for_json({
            "message": "CSV cleaned successfully",
            "file_id": file_id,
            "original_rows": len(df),
            "cleaned_rows": len(cleaned_df),
            "columns": len(cleaned_df.columns),
            "cleaning_report": report,
            "download_endpoint": f"/download/{file_id}"
        })

    except FileNotFoundError:
        raise HTTPException(404, "Uploaded CSV file not found")

    except ValueError as error:
        raise HTTPException(400, str(error))

    except PyMongoError:
        raise HTTPException(503, "Database error")


# 8. Download cleaned CSV (protected)
@router.get("/download/{file_id}")
def download_cleaned_csv(
    file_id: str,
    current_user: str = Depends(get_current_user)
):

    try:
        dataset = get_dataset(file_id)

        if not dataset:
            raise HTTPException(404, "Dataset not found")

        cleaned_path = dataset.get("cleaned_path")

        if not cleaned_path or not Path(cleaned_path).is_file():
            raise HTTPException(404, "Cleaned CSV file not found")

        filename = (
            Path(dataset["filename"]).stem + "_cleaned.csv"
        )

        return FileResponse(
            path=cleaned_path,
            media_type="text/csv",
            filename=filename
        )

    except PyMongoError:
        raise HTTPException(503, "Database error")
