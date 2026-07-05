"""
views/upload.py

Journal upload page.
"""

from pathlib import Path

import streamlit as st

from auth.database import SessionLocal
from auth.models import UploadedFile
from rag.embeddings import delete_file_chunks
from rag.ingest import ingest_document
from utils.file_utils import (
    calculate_sha256,
    get_file_extension,
    is_supported_file,
    save_uploaded_file,
)


def show_upload_page(user):
    """
    Display the upload page.
    """

    st.title("📂 Upload Journals")

    st.write(
        "Upload your journal files.\n"
        "Supported formats: TXT, MD, PDF, DOCX."
    )

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["txt", "md", "pdf", "docx"],
    )

    # =====================================================
    # Upload
    # =====================================================

    if uploaded_file is not None:

        db = SessionLocal()

        try:

            # ----------------------------
            # Validate file type
            # ----------------------------

            if not is_supported_file(uploaded_file.name):

                st.error("Unsupported file type.")
                return

            # ----------------------------
            # Calculate hash
            # ----------------------------

            file_hash = calculate_sha256(uploaded_file)

            # ----------------------------
            # Duplicate detection
            # ----------------------------

            duplicate = (
                db.query(UploadedFile)
                .filter(
                    UploadedFile.user_id == user.id,
                    UploadedFile.sha256 == file_hash,
                )
                .first()
            )

            if duplicate:

                st.warning(
                    "This journal has already been uploaded."
                )
                return

            # ----------------------------
            # Save file
            # ----------------------------

            saved_path = save_uploaded_file(
                uploaded_file,
                user.id,
            )

            # ----------------------------
            # Database record
            # ----------------------------

            db_file = UploadedFile(
                user_id=user.id,
                original_name=uploaded_file.name,
                stored_name=saved_path.name,
                sha256=file_hash,
                file_type=get_file_extension(
                    uploaded_file.name
                ),
                file_size=uploaded_file.size,
                indexed=False,
                chunk_count=0,
            )

            db.add(db_file)
            db.commit()
            db.refresh(db_file)

            # ----------------------------
            # Index
            # ----------------------------

            with st.spinner(
                "Indexing your journal..."
            ):

                ingest_document(db_file.id)

            st.success(
                f"✅ {uploaded_file.name} uploaded successfully!"
            )

            st.rerun()

        except Exception as e:

            db.rollback()

            st.error(
                f"Upload failed:\n\n{e}"
            )

        finally:

            db.close()

    # =====================================================
    # Uploaded Journals
    # =====================================================

    st.divider()

    st.subheader("📚 Your Uploaded Journals")

    db = SessionLocal()

    files = (
        db.query(UploadedFile)
        .filter(
            UploadedFile.user_id == user.id
        )
        .order_by(
            UploadedFile.uploaded_at.desc()
        )
        .all()
    )

    if not files:

        st.info(
            "No journals uploaded yet."
        )

    else:

        for file in files:

            col1, col2 = st.columns([8, 1])

            with col1:

                size_mb = file.file_size / (1024 * 1024)

                st.markdown(
                    f"**📄 {file.original_name}**"
                )

                st.caption(
                    f"{size_mb:.2f} MB • "
                    f"{file.uploaded_at.strftime('%Y-%m-%d %H:%M')}"
                )

            with col2:

                if st.button(
                    "🗑",
                    key=f"delete_{file.id}",
                    help="Delete journal",
                ):

                    try:

                        # ----------------------------
                        # Delete vectors
                        # ----------------------------

                        delete_file_chunks(
                            user_id=user.id,
                            file_id=file.id,
                        )

                        # ----------------------------
                        # Delete physical file
                        # ----------------------------

                        upload_path = (
                            Path("storage")
                            / str(user.id)
                            / "uploads"
                            / file.stored_name
                        )

                        if upload_path.exists():

                            upload_path.unlink()

                        # ----------------------------
                        # Delete database record
                        # ----------------------------

                        db.delete(file)
                        db.commit()

                        st.success(
                            "Journal deleted successfully."
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Delete failed:\n\n{e}"
                        )

    db.close()