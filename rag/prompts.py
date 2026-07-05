"""
rag/prompts.py

Prompt templates for Roast My Past Self.
"""

from typing import Dict, List

# ---------------------------------------------------
# Normal Prompt
# ---------------------------------------------------

SYSTEM_PROMPT = """
You are the user's past self.

You answer ONLY using the journal entries provided as context.

Rules:

1. Speak naturally in first person whenever appropriate.
2. Never invent facts.
3. If the answer is not present in the retrieved journal entries,
   clearly say you don't have enough information.
4. Mention the journal filename whenever helpful.
5. If multiple journal entries describe the same situation,
   point out the recurring pattern.
6. If retrieved entries contradict each other,
   politely mention the contradiction.
7. Keep answers conversational.
8. Do not mention embeddings, retrieval, vector databases,
   or implementation details.
"""

# ---------------------------------------------------
# Roast Prompt
# ---------------------------------------------------

ROAST_PROMPT = """
You are the user's brutally honest past self.

You answer ONLY using the journal entries provided as context.

Your personality:

- Funny
- Witty
- Sarcastic
- Honest
- Self-aware

Rules:

1. Roast the user's recurring habits in a playful way.
2. Point out repeated excuses and patterns.
3. Mention contradictions if they exist.
4. Never invent facts.
5. Never be mean, abusive, or insulting.
6. Base every observation on the retrieved journal entries.
7. If there isn't enough evidence, say so.
8. Reference the filenames whenever useful.
"""

# ---------------------------------------------------
# Context Builder
# ---------------------------------------------------

def build_context(chunks: List[Dict]) -> str:
    """
    Convert retrieved chunks into readable context.
    """

    context = []

    for i, chunk in enumerate(chunks, start=1):

        filename = chunk.get("filename", "Unknown")
        entry = chunk.get("entry_index", "-")
        text = chunk.get("text", "")

        context.append(
            f"""
Source {i}
Filename: {filename}
Entry: {entry}

{text}
"""
        )

    return "\n".join(context)


# ---------------------------------------------------
# Normal Prompt Builder
# ---------------------------------------------------

def build_prompt(
    question: str,
    chunks: List[Dict],
) -> str:
    """
    Build the normal assistant prompt.
    """

    context = build_context(chunks)

    return f"""
{SYSTEM_PROMPT}

=========================
Journal Entries
=========================

{context}

=========================
User Question
=========================

{question}

=========================
Assistant Answer
=========================
"""


# ---------------------------------------------------
# Roast Prompt Builder
# ---------------------------------------------------

def build_roast_prompt(
    question: str,
    chunks: List[Dict],
) -> str:
    """
    Build the roast mode prompt.
    """

    context = build_context(chunks)

    return f"""
{ROAST_PROMPT}

=========================
Journal Entries
=========================

{context}

=========================
User Question
=========================

{question}

=========================
Roast
=========================
"""