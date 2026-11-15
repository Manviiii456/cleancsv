
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from uuid import uuid4
from pymongo.errors import PyMongoError

from backend.file_handler import (
    read_csv_file,
    save_uploaded_file
)

from backend.database import (
    add_dataset,
    get_dataset,
    get_history
)

router = APIRouter()


# Health check
@router.get("/health")
def health_check():
    return {
        "message": "CleanCSV API is working",
        "status": "Healthy"
    }


# Upload CSV file
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

        # Save original CSV in storage/uploads
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


# Get details of one uploaded CSV
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


# View upload history
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
