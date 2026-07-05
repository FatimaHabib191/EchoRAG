"""
rag/splitter.py

Splits journal documents into entries and chunks.

Workflow:

Document
    ↓
Detect journal entries
    ↓
Split long entries into chunks
    ↓
Return chunks with metadata
"""

from __future__ import annotations

import re
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter


# ----------------------------------------------------
# Chunking configuration
# ----------------------------------------------------

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150


# Common journal date patterns
DATE_PATTERNS = [
    r"\d{4}-\d{2}-\d{2}",                     # 2026-07-05
    r"\d{2}/\d{2}/\d{4}",                     # 05/07/2026
    r"\d{2}-\d{2}-\d{4}",                     # 05-07-2026
    r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}",
]


splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=[
        "\n\n",
        "\n",
        ". ",
        " ",
        "",
    ],
)


def detect_entries(text: str) -> List[str]:
    """
    Detects multiple journal entries inside a document.

    If no obvious date separators are found,
    returns the entire document as one entry.
    """

    pattern = "|".join(DATE_PATTERNS)

    matches = list(
        re.finditer(pattern, text, flags=re.IGNORECASE)
    )

    if len(matches) <= 1:
        return [text.strip()]

    entries = []

    for i, match in enumerate(matches):

        start = match.start()

        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(text)

        entry = text[start:end].strip()

        if entry:
            entries.append(entry)

    return entries


def chunk_entry(entry: str) -> List[str]:
    """
    Splits one journal entry into chunks.
    """

    return splitter.split_text(entry)


def split_document(text: str) -> List[dict]:
    """
    Splits an entire document into chunks.

    Returns:

    [
        {
            "entry_index": 1,
            "chunk_index": 1,
            "text": "...",
        },
        ...
    ]
    """

    entries = detect_entries(text)

    chunks = []

    for entry_number, entry in enumerate(entries):

        entry_chunks = chunk_entry(entry)

        for chunk_number, chunk in enumerate(entry_chunks):

            chunks.append(
                {
                    "entry_index": entry_number,
                    "chunk_index": chunk_number,
                    "text": chunk,
                }
            )

    return chunks


def count_chunks(text: str) -> int:
    """
    Returns how many chunks would be generated.
    """

    return len(split_document(text))