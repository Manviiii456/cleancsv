
import os
from pymongo import MongoClient
from datetime import datetime

# MongoDB connection
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://localhost:27017/"
)

client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000
)

# Database
db = client["cleancsv"]

# Collection
datasets_collection = db["datasets"]


# Check MongoDB connection
def initialize_database():
    client.admin.command("ping")

    datasets_collection.create_index(
        "file_id",
        unique=True
    )

    print("MongoDB connected successfully!")


# Save uploaded CSV details
def add_dataset(file_id, filename, original_path, rows, columns):

    dataset = {
        "file_id": file_id,
        "filename": filename,
        "original_path": str(original_path),
        "cleaned_path": None,
        "rows": rows,
        "columns": columns,
        "uploaded_at": datetime.now(),
        "cleaned_at": None
    }

    datasets_collection.insert_one(dataset)


# Get one uploaded dataset
def get_dataset(file_id):

    return datasets_collection.find_one(
        {"file_id": file_id},
        {"_id": 0}
    )


# Update cleaned CSV details
def update_cleaned_file(file_id, cleaned_path):

    datasets_collection.update_one(
        {"file_id": file_id},
        {
            "$set": {
                "cleaned_path": str(cleaned_path),
                "cleaned_at": datetime.now()
            }
        }
    )


# Get upload history
def get_history():

    return list(
        datasets_collection.find(
            {},
            {"_id": 0}
        ).sort("uploaded_at", -1)
    )
