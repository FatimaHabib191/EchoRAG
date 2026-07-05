from __future__ import annotations

import hashlib
import shutil
import uuid
from pathlib import Path

import streamlit as st

from config import STORAGE_DIR


SUPPORTED_EXTENSIONS = {
    ".txt",
    ".md",
    ".pdf",
    ".docx",
}


def get_user_upload_directory(user_id: str) -> Path:
    """
    Returns the upload directory for a user.
    Creates it if it doesn't exist.
    """

    upload_dir = STORAGE_DIR / user_id / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)

    return upload_dir


def get_file_extension(filename: str) -> str:
    """
    Returns the file extension in lowercase.
    """

    return Path(filename).suffix.lower()


def is_supported_file(filename: str) -> bool:
    """
    Checks whether the uploaded file type is supported.
    """

    return get_file_extension(filename) in SUPPORTED_EXTENSIONS


def calculate_sha256(uploaded_file) -> str:
    """
    Calculates the SHA-256 hash of the uploaded file.
    """

    uploaded_file.seek(0)

    sha256 = hashlib.sha256()

    while chunk := uploaded_file.read(8192):
        sha256.update(chunk)

    uploaded_file.seek(0)

    return sha256.hexdigest()


def generate_stored_filename(original_filename: str) -> str:
    """
    Generates a unique filename while preserving the extension.
    """

    extension = get_file_extension(original_filename)

    return f"{uuid.uuid4()}{extension}"


def save_uploaded_file(uploaded_file, user_id: str) -> Path:
    """
    Saves the uploaded file to the user's upload directory.
    """

    upload_dir = get_user_upload_directory(user_id)

    stored_filename = generate_stored_filename(
        uploaded_file.name
    )

    destination = upload_dir / stored_filename

    uploaded_file.seek(0)

    with open(destination, "wb") as f:
        shutil.copyfileobj(uploaded_file, f)

    uploaded_file.seek(0)

    return destination