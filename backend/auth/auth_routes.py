
from datetime import datetime, timedelta, timezone
import os

import jwt
from pwdlib import PasswordHash
from pymongo.errors import DuplicateKeyError

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.database import (
    add_user,
    get_user_by_email,
    users_collection
)


# Authentication router
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# Password hashing
password_hash = PasswordHash.recommended()

# JWT configuration
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "cleancsv-demo-secret-change-before-deployment"
)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# =====================================
# REQUEST MODELS
# =====================================

class RegisterRequest(BaseModel):
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: str
    password: str


class ResetPasswordRequest(BaseModel):
    email: str = Field(min_length=5, max_length=254)
    new_password: str = Field(min_length=8, max_length=128)


# =====================================
# CREATE JWT TOKEN
# =====================================

def create_access_token(email: str):

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": email,
        "exp": expire
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


# =====================================
# USER REGISTRATION API
# =====================================

@router.post("/register")
def register_user(user: RegisterRequest):

    email = user.email.strip().lower()

    if "@" not in email or "." not in email.split("@")[-1]:
        raise HTTPException(
            status_code=400,
            detail="Please enter a valid email address"
        )

    hashed_password = password_hash.hash(user.password)

    try:

        add_user(email, hashed_password)

        return {
            "message": "Registration successful",
            "email": email
        }

    except DuplicateKeyError:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )


# =====================================
# USER LOGIN API
# =====================================

@router.post("/login")
def login_user(user: LoginRequest):

    email = user.email.strip().lower()

    existing_user = get_user_by_email(email)

    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not password_hash.verify(
        user.password,
        existing_user["hashed_password"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_access_token(email)

    return {
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer",
        "email": email
    }


# =====================================
# FORGOT PASSWORD API
# =====================================

@router.post("/reset-password")
def reset_password(user: ResetPasswordRequest):

    email = user.email.strip().lower()

    if "@" not in email or "." not in email.split("@")[-1]:
        raise HTTPException(
            status_code=400,
            detail="Please enter a valid email address"
        )

    # Check whether email exists
    existing_user = get_user_by_email(email)

    if not existing_user:
        raise HTTPException(
            status_code=404,
            detail="Email address is not registered"
        )

    # Hash the new password
    hashed_password = password_hash.hash(user.new_password)

    # Update password in MongoDB
    result = users_collection.update_one(
        {"email": email},
        {
            "$set": {
                "hashed_password": hashed_password,
                "password_updated_at": datetime.now(timezone.utc)
            }
        }
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "message": "Password reset successful! Please login with your new password."
    }
