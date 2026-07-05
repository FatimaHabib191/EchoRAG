"""
views/settings.py

User settings.
"""

import shutil

import streamlit as st

from auth.database import SessionLocal
from auth.models import UploadedFile, User
from config import STORAGE_DIR
from rag.embeddings import delete_collection


def show_settings_page(user):
    """
    Display settings page.
    """

    st.title("⚙ Settings")

    st.subheader("Account")

    st.text_input(
        "Username",
        value=user.username,
        disabled=True,
    )

    st.text_input(
        "Email",
        value=user.email,
        disabled=True,
    )

    st.divider()

    st.subheader("Storage")

    st.write(
        "Manage your uploaded journals."
    )

    db = SessionLocal()

    # -------------------------------------------------
    # Delete All Uploaded Files
    # -------------------------------------------------

    if st.button(
        "🗑 Delete All Uploaded Files",
        use_container_width=True,
    ):

        try:

            # Delete vectors
            delete_collection(user.id)

            # Delete database records
            db.query(UploadedFile).filter(
                UploadedFile.user_id == user.id
            ).delete()

            db.commit()

            # Delete uploaded files only
            uploads_folder = (
                STORAGE_DIR
                / user.id
                / "uploads"
            )

            if uploads_folder.exists():
                shutil.rmtree(
                    uploads_folder,
                    ignore_errors=True,
                )

            uploads_folder.mkdir(
                parents=True,
                exist_ok=True,
            )

            st.success(
                "All uploaded journals deleted successfully."
            )

        except Exception as e:

            st.warning(
                f"Some files were already removed. ({e})"
            )

    st.divider()

    st.subheader("Danger Zone")

    # -------------------------------------------------
    # Delete Account
    # -------------------------------------------------

    if st.button(
        "Delete My Account",
        type="primary",
        use_container_width=True,
    ):

        try:

            delete_collection(user.id)

            db.query(UploadedFile).filter(
                UploadedFile.user_id == user.id
            ).delete()

            db.query(User).filter(
                User.id == user.id
            ).delete()

            db.commit()

            user_folder = STORAGE_DIR / user.id

            if user_folder.exists():
                shutil.rmtree(
                    user_folder,
                    ignore_errors=True,
                )

            st.session_state.logged_in = False
            st.session_state.user = None

            st.success(
                "Your account has been deleted."
            )

            st.rerun()

        except Exception as e:

            st.error(
                f"Failed to delete account.\n\n{e}"
            )

    db.close()