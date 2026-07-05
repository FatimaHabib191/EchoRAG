"""
rag/embeddings.py

Handles:
- Loading the embedding model
- Creating user-specific Chroma collections
- Storing journal chunks
- Semantic search
"""

from __future__ import annotations

from pathlib import Path
from typing import List

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from config import STORAGE_DIR


# ---------------------------------------------------
# Embedding Model
# ---------------------------------------------------

MODEL_NAME = "BAAI/bge-small-en-v1.5"

_embedding_model = SentenceTransformer(MODEL_NAME)


# ---------------------------------------------------
# Embedding Functions
# ---------------------------------------------------

def embed_text(text: str) -> List[float]:
    """
    Generate an embedding for a single piece of text.
    """

    embedding = _embedding_model.encode(
        text,
        normalize_embeddings=True,
    )

    return embedding.tolist()


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for multiple texts in one batch.
    """

    embeddings = _embedding_model.encode(
        texts,
        normalize_embeddings=True,
    )

    return embeddings.tolist()


# ---------------------------------------------------
# ChromaDB
# ---------------------------------------------------

def get_user_chroma_client(user_id: str):
    """
    Returns a persistent Chroma client for the user.
    """

    chroma_path = STORAGE_DIR / user_id / "chroma"

    chroma_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    return chromadb.PersistentClient(
        path=str(chroma_path),
        settings=Settings(
            anonymized_telemetry=False,
        ),
    )


def get_collection(user_id: str):
    """
    Returns the user's journal collection.
    """

    client = get_user_chroma_client(user_id)

    return client.get_or_create_collection(
        name="journal_entries",
    )


# ---------------------------------------------------
# Store Chunks
# ---------------------------------------------------

def add_chunks(
    user_id: str,
    chunks: List[dict],
    metadata: List[dict],
):
    """
    Store journal chunks in ChromaDB.
    """

    collection = get_collection(user_id)

    # Extract all texts
    documents = [chunk["text"] for chunk in chunks]

    # Batch embedding (much faster)
    embeddings = embed_texts(documents)

    # IDs for Chroma
    ids = [item["id"] for item in metadata]

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadata,
    )


# ---------------------------------------------------
# Search
# ---------------------------------------------------

def similarity_search(
    user_id: str,
    query: str,
    top_k: int = 5,
):
    """
    Perform semantic similarity search.
    """

    collection = get_collection(user_id)

    query_embedding = embed_text(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )

    return results


# ---------------------------------------------------
# Utilities
# ---------------------------------------------------

def collection_size(user_id: str) -> int:
    """
    Returns the number of indexed chunks.
    """

    collection = get_collection(user_id)

    return collection.count()


def delete_collection(user_id: str):
    """
    Deletes the user's Chroma collection.
    """

    client = get_user_chroma_client(user_id)

    try:
        client.delete_collection("journal_entries")
    except Exception:
        pass
    # ---------------------------------------------------
# Delete Chunks for One File
# ---------------------------------------------------

def delete_file_chunks(
    user_id: str,
    file_id: str,
):
    """
    Delete all chunks belonging to a single uploaded file.
    """

    collection = get_collection(user_id)

    try:

        collection.delete(
            where={
                "file_id": file_id
            }
        )

    except Exception:
        pass