"""
rag/loaders.py

Loads supported document types and returns extracted text.

Supported formats:
- .txt
- .md
- .pdf
- .docx
"""

from pathlib import Path

from pypdf import PdfReader
from docx import Document


SUPPORTED_EXTENSIONS = {
    ".txt",
    ".md",
    ".pdf",
    ".docx",
}


class UnsupportedFileTypeError(Exception):
    """Raised when an unsupported file type is encountered."""
    pass


def load_text_file(file_path: Path) -> str:
    """
    Load a plain text or markdown file.
    """

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def load_pdf(file_path: Path) -> str:
    """
    Extract text from a PDF.
    """

    reader = PdfReader(file_path)

    pages = []

    for page in reader.pages:

        text = page.extract_text()

        if text:
            pages.append(text)

    return "\n".join(pages)


def load_docx(file_path: Path) -> str:
    """
    Extract text from a DOCX document.
    """

    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:

        if paragraph.text.strip():

            paragraphs.append(paragraph.text)

    return "\n".join(paragraphs)


def get_extension(file_path: Path) -> str:
    """
    Returns the lowercase file extension.
    """

    return file_path.suffix.lower()


def load_document(file_path: Path) -> str:
    """
    Loads any supported document and returns extracted text.
    """

    extension = get_extension(file_path)

    if extension not in SUPPORTED_EXTENSIONS:

        raise UnsupportedFileTypeError(
            f"Unsupported file type: {extension}"
        )

    if extension in [".txt", ".md"]:
        return load_text_file(file_path)

    if extension == ".pdf":
        return load_pdf(file_path)

    if extension == ".docx":
        return load_docx(file_path)

    raise UnsupportedFileTypeError(extension)


def validate_document(file_path: Path) -> bool:
    """
    Returns True if the file is supported.
    """

    return get_extension(file_path) in SUPPORTED_EXTENSIONS