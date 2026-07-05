"""
rag/retriever.py

Retrieves the most relevant journal chunks from ChromaDB.
"""

from __future__ import annotations

from typing import Dict, List

from rag.embeddings import similarity_search


def retrieve_context(
    user_id: str,
    query: str,
    top_k: int = 5,
) -> List[Dict]:
    """
    Retrieve the most relevant journal chunks for a query.

    Returns:
    [
        {
            "text": "...",
            "filename": "...",
            "file_id": "...",
            "entry_index": 0,
            "chunk_index": 1,
            "score": 0.23,
        }
    ]
    """

    results = similarity_search(
        user_id=user_id,
        query=query,
        top_k=top_k,
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    # Depending on Chroma version this may be "distances"
    # or may not exist.
    distances = results.get(
        "distances",
        [[0.0] * len(documents)]
    )[0]

    retrieved_chunks = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances,
    ):

        retrieved_chunks.append(
            {
                "text": document,
                "filename": metadata.get(
                    "filename",
                    "Unknown"
                ),
                "file_id": metadata.get(
                    "file_id"
                ),
                "entry_index": metadata.get(
                    "entry_index"
                ),
                "chunk_index": metadata.get(
                    "chunk_index"
                ),
                "score": round(float(distance), 4),
            }
        )

    return retrieved_chunks


def retrieve_text_only(
    user_id: str,
    query: str,
    top_k: int = 5,
) -> List[str]:
    """
    Returns only the retrieved texts.
    Useful for debugging.
    """

    chunks = retrieve_context(
        user_id,
        query,
        top_k,
    )

    return [
        chunk["text"]
        for chunk in chunks
    ]


def print_retrieved_chunks(
    chunks: List[Dict],
):
    """
    Pretty-print retrieved chunks.
    Useful while developing.
    """

    print("\nRetrieved Chunks\n")

    for i, chunk in enumerate(
        chunks,
        start=1,
    ):

        print("-" * 60)

        print(f"Chunk {i}")

        print(
            f"File : {chunk['filename']}"
        )

        print(
            f"Entry: {chunk['entry_index']}"
        )

        print(
            f"Chunk: {chunk['chunk_index']}"
        )

        print(
            f"Score: {chunk['score']}"
        )

        print()

        print(chunk["text"])

        print()