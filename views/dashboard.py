"""
views/dashboard.py

Main dashboard and application navigation.
"""

from pathlib import Path

import streamlit as st

from auth.database import SessionLocal
from auth.models import UploadedFile
from views.upload import show_upload_page
from views.chat import show_chat_page
from views.insights import show_insights_page
from views.settings import show_settings_page


def show_dashboard():
    """
    Main dashboard after login.
    """

    user = st.session_state.user

    db = SessionLocal()

    uploaded_files = (
        db.query(UploadedFile)
        .filter(
            UploadedFile.user_id == user.id
        )
        .order_by(
            UploadedFile.uploaded_at.desc()
        )
        .all()
    )

    total_files = len(uploaded_files)

    total_size = sum(
        file.file_size for file in uploaded_files
    )

    total_size_mb = round(
        total_size / (1024 * 1024),
        2
    )

    # -------------------------
    # Sidebar
    # -------------------------

    with st.sidebar:

        st.title("Explore your memories through AI.")

        st.write(f"Welcome **{user.username}**")

        page = st.radio(
            "Navigation",
            [
                "Dashboard",
                "Upload",
                "Chat",
                "Insights",
                "Settings",
            ],
        )

        st.divider()

        if st.button(
            "Logout",
            use_container_width=True,
        ):

            db.close()

            st.session_state.logged_in = False
            st.session_state.user = None

            st.rerun()

    # -------------------------
    # Dashboard
    # -------------------------

    if page == "Dashboard":

        st.title("🏠 Dashboard")

        st.write(
            "Welcome back! Here's an overview of your journals."
        )

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

        st.subheader("Recent Uploads")

        if not uploaded_files:

            st.info(
                "No journals uploaded yet."
            )

        else:

            for file in uploaded_files[:5]:

                st.write(
                    f"📄 {file.original_name}"
                )

    # -------------------------
    # Upload
    # -------------------------

    elif page == "Upload":

        show_upload_page(user)

    # -------------------------
    # Chat
    # -------------------------

    elif page == "Chat":

        show_chat_page(user)

    # -------------------------
    # Insights
    # -------------------------

    elif page == "Insights":

        show_insights_page(user)

    # -------------------------
    # Settings
    # -------------------------

    elif page == "Settings":

        show_settings_page(user)

    db.close()