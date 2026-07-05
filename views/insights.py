"""
views/insights.py

Displays journal statistics.
"""

import streamlit as st

from auth.database import SessionLocal
from auth.models import UploadedFile


def show_insights_page(user):
    """
    Display journal insights.
    """

    st.title("📈 Insights")

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

    total_files = len(files)

    total_size = sum(
        file.file_size for file in files
    )

    total_size_mb = round(
        total_size / (1024 * 1024),
        2
    )

    st.subheader("Statistics")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Uploaded Files",
            total_files,
        )

    with col2:
        st.metric(
            "Storage Used",
            f"{total_size_mb} MB",
        )

    st.divider()

    st.subheader("Uploaded Journals")

    if not files:

        st.info(
            "No journals uploaded yet."
        )

    else:

        for file in files:

            st.write(
                f"📄 {file.original_name}"
            )

    st.divider()

    st.subheader("Supported Formats")

    st.markdown("""
- TXT
- MD
- PDF
- DOCX
""")

    db.close()