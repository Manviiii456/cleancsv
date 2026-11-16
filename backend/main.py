
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import router
from backend.database import initialize_database


# Create FastAPI application
app = FastAPI(
    title="CleanCSV",
    description="Automatic CSV Data Cleaning and Quality Analysis System",
    version="1.0.0"
)


# Enable frontend-backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Connect to MongoDB when backend starts
@app.on_event("startup")
def startup_event():
    initialize_database()


# Connect all API routes
app.include_router(router)


# Home API
@app.get("/")
def home():
    return {
        "message": "Welcome to CleanCSV API",
        "database": "MongoDB",
        "status": "Connected"
    }
