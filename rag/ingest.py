"""
rag/ingest.py

Coordinates the complete indexing pipeline.

Pipeline:

Document
    ↓
Load
    ↓
Split
    ↓
Generate Embeddings
    ↓
Store in Chroma
    ↓
Update SQLite
"""

from __future__ import annotations

import uuid
from pathlib import Path

from auth.database import SessionLocal
from auth.models import UploadedFile

from rag.embeddings import add_chunks
from rag.loaders import load_document
from rag.splitter import split_document
from config import STORAGE_DIR

def ingest_document(file_id: str):
    """
    Indexes a single uploaded document into ChromaDB.
    """

    db = SessionLocal()

    try:

        uploaded_file = (
            db.query(UploadedFile)
            .filter(UploadedFile.id == file_id)
            .first()
        )

        if uploaded_file is None:
            raise ValueError("Uploaded file not found.")

        file_path = (
            STORAGE_DIR
            / uploaded_file.user_id
            / "uploads"
            / uploaded_file.stored_name
        )

        # -------------------------
        # Load document
        # -------------------------

        text = load_document(file_path)

        # -------------------------
        # Split document
        # -------------------------

        chunks = split_document(text)

        # -------------------------
        # Prepare metadata
        # -------------------------

        metadata = []

        for chunk in chunks:

            metadata.append(
                {
                    "id": str(uuid.uuid4()),
                    "file_id": uploaded_file.id,
                    "filename": uploaded_file.original_name,
                    "user_id": uploaded_file.user_id,
                    "entry_index": chunk["entry_index"],
                    "chunk_index": chunk["chunk_index"],
                }
            )

        # -------------------------
        # Store embeddings
        # -------------------------

        add_chunks(
            user_id=uploaded_file.user_id,
            chunks=chunks,
            metadata=metadata,
        )

        # -------------------------
        # Update database
        # -------------------------

        uploaded_file.indexed = True
        uploaded_file.chunk_count = len(chunks)

        db.commit()

    except Exception:

        db.rollback()
        raise

    finally:

        db.close()