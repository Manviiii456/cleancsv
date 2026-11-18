
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

# Collections
datasets_collection = db["datasets"]
users_collection = db["users"]


# Initialize MongoDB
def initialize_database():
    try:
        client.admin.command("ping")

        # Dataset unique index
        datasets_collection.create_index(
            "file_id",
            unique=True
        )

        # User email unique index
        users_collection.create_index(
            "email",
            unique=True
        )

        print("MongoDB connected successfully!")

    except Exception as error:
        print(f"MongoDB connection failed: {error}")
        raise


# -------------------------------
# EXISTING DATASET FUNCTIONS
# -------------------------------

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


def get_dataset(file_id):

    return datasets_collection.find_one(
        {"file_id": file_id},
        {"_id": 0}
    )


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


def get_history():

    return list(
        datasets_collection.find(
            {},
            {"_id": 0}
        ).sort("uploaded_at", -1)
    )


# -------------------------------
# NEW USER AUTHENTICATION FUNCTIONS
# -------------------------------

# Register a new user
def add_user(email, hashed_password):

    user = {
        "email": email,
        "hashed_password": hashed_password,
        "created_at": datetime.now()
    }

    return users_collection.insert_one(user)


# Find user using email
def get_user_by_email(email):

    return users_collection.find_one(
        {"email": email}
    )
