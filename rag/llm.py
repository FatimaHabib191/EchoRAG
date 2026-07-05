"""
rag/llm.py

Handles communication with Google Gemini.
"""

from __future__ import annotations

import os

import google.generativeai as genai
from dotenv import load_dotenv

from rag.prompts import (
    build_prompt,
    build_roast_prompt,
)
from rag.retriever import retrieve_context


# ---------------------------------------------------
# Load Environment
# ---------------------------------------------------

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found in .env file."
    )

genai.configure(api_key=api_key)


# ---------------------------------------------------
# Gemini Model
# ---------------------------------------------------

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)


# ---------------------------------------------------
# Main Function
# ---------------------------------------------------

def ask_past_self(
    user_id: str,
    question: str,
    roast_mode: bool = False,
    top_k: int = 5,
):
    """
    Ask the user's journals a question.

    Returns:

    {
        "answer": "...",
        "sources": [...]
    }
    """

    # ---------------------------------------
    # Retrieve Context
    # ---------------------------------------

    chunks = retrieve_context(
        user_id=user_id,
        query=question,
        top_k=top_k,
    )

    if not chunks:

        return {
            "answer":
                "I couldn't find anything relevant in your journals.",
            "sources": [],
        }

    # ---------------------------------------
    # Select Prompt
    # ---------------------------------------

    if roast_mode:

        prompt = build_roast_prompt(
            question=question,
            chunks=chunks,
        )

    else:

        prompt = build_prompt(
            question=question,
            chunks=chunks,
        )

    # ---------------------------------------
    # Generate Response
    # ---------------------------------------

    try:

        response = model.generate_content(
            prompt
        )

        answer = response.text.strip()

    except Exception as e:

        answer = (
            "Sorry, something went wrong while "
            f"generating the response.\n\n{e}"
        )

    return {
        "answer": answer,
        "sources": chunks,
    }