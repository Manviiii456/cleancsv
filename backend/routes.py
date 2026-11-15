
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from uuid import uuid4
from pymongo.errors import PyMongoError

# File handling functions
from backend.file_handler import (
    read_csv_file,
    save_uploaded_file,
    get_uploaded_file
)

# Data analysis functions - Member 2
from backend.analysis.data_analyzer import analyze_csv
from backend.analysis.data_validator import validate_data
from backend.analysis.missing_values import detect_missing_values
from backend.analysis.duplicate_detector import detect_duplicates
from backend.analysis.outlier_detector import detect_outliers

# Database functions
from backend.database import (
    add_dataset,
    get_dataset,
    get_history
)

router = APIRouter()


# 1. Health check
@router.get("/health")
def health_check():
    return {
        "message": "CleanCSV API is working",
        "status": "Healthy"
    }


# 2. Upload CSV file
@router.post("/upload")
async def upload_csv(file: UploadFile = File(...)):

    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are allowed"
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty"
        )

    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File size must be below 10 MB"
        )

    try:
        # Read and validate CSV
        df = read_csv_file(content)

        # Generate unique file ID
        file_id = str(uuid4())

        # Save original CSV
        file_path = save_uploaded_file(
            file_id,
            content
        )

        # Save file details in MongoDB
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
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except PyMongoError:
        raise HTTPException(
            status_code=503,
            detail="Unable to save file details in MongoDB"
        )


# 3. Get details of one uploaded CSV
@router.get("/dataset/{file_id}")
def dataset_details(file_id: str):

    try:
        dataset = get_dataset(file_id)

        if not dataset:
            raise HTTPException(
                status_code=404,
                detail="Dataset not found"
            )

        return dataset

    except PyMongoError:
        raise HTTPException(
            status_code=503,
            detail="Unable to retrieve dataset from MongoDB"
        )


# 4. View upload history
@router.get("/history")
def upload_history():

    try:
        return {
            "history": get_history()
        }

    except PyMongoError:
        raise HTTPException(
            status_code=503,
            detail="Unable to retrieve upload history"
        )


# 5. Analyze uploaded CSV
@router.get("/analysis/{file_id}")
def analyze_dataset(file_id: str):

    try:
        # Check dataset in MongoDB
        dataset = get_dataset(file_id)

        if not dataset:
            raise HTTPException(
                status_code=404,
                detail="Dataset not found"
            )

        # Get uploaded CSV file
        file_path = get_uploaded_file(file_id)

        # Read CSV
        df = read_csv_file(file_path.read_bytes())

        # Validate dataset
        validation = validate_data(df)

        if not validation["is_valid"]:
            raise HTTPException(
                status_code=400,
                detail=validation["errors"]
            )

        # Perform basic analysis
        analysis = analyze_csv(str(file_path))

        if "error" in analysis:
            raise HTTPException(
                status_code=400,
                detail=analysis["error"]
            )

        # Detect missing values
        missing = detect_missing_values(df)

        # Detect duplicate records
        duplicates = detect_duplicates(df)

        # Detect outliers
        outliers = detect_outliers(df)

        return {
            "file_id": file_id,
            "filename": dataset["filename"],
            "validation": validation,
            "analysis": analysis,
            "missing_values": missing,
            "duplicates": duplicates,
            "outliers": outliers
        }

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Uploaded CSV file not found"
        )

    except PyMongoError:
        raise HTTPException(
            status_code=503,
            detail="Database error"
        )
