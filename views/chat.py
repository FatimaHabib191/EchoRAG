"""
views/chat.py

Chat interface for Roast My Past Self.
"""

import streamlit as st

from auth.database import SessionLocal
from auth.models import UploadedFile
from rag.llm import ask_past_self


def show_chat_page(user):
    """
    Display the chat page.
    """

    st.title("💬 Chat With Your Past Self")

    db = SessionLocal()

    uploaded_files = (
        db.query(UploadedFile)
        .filter(
            UploadedFile.user_id == user.id,
            UploadedFile.indexed == True
        )
        .all()
    )

    db.close()

    if not uploaded_files:

        st.warning(
            "Upload at least one journal before chatting."
        )
        return

    # -------------------------------------------------
    # Chat Controls
    # -------------------------------------------------

    col1, col2 = st.columns([3, 1])

    with col1:

        mode = st.radio(
    "Conversation Mode",
    [
        "Reflect",
        "Roast 🔥",
        "Then vs Now ⏳",
    ],
    horizontal=True,
)

    with col2:

        if st.button(
            "🗑 Clear Chat",
            use_container_width=True,
        ):

            st.session_state[f"messages_{user.id}"] = []
            st.rerun()

    st.divider()

    # -------------------------------------------------
    # Chat History
    # -------------------------------------------------

    history_key = f"messages_{user.id}"

    if history_key not in st.session_state:
        st.session_state[history_key] = []

    messages = st.session_state[history_key]

    for message in messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

            if (
                message["role"] == "assistant"
                and message.get("sources")
            ):

                with st.expander("📚 Sources"):

                    for source in message["sources"]:

                        with st.container(border=True):

                            st.markdown(
                                f"**📄 {source['filename']}**"
                            )

                            st.caption(
                                f"Entry {source['entry_index']}"
                            )

                            st.write(source["text"])

    # -------------------------------------------------
    # User Input
    # -------------------------------------------------

    question = st.chat_input(
        "Ask your past self something..."
    )

    if not question:
        return

    # Save user message

    messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):

        st.markdown(question)

    # -------------------------------------------------
    # AI Response
    # -------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            result = ask_past_self(
                user_id=user.id,
                question=question,
                roast_mode=roast_mode,
            )

        st.markdown(result["answer"])

        if result["sources"]:

            with st.expander("📚 Sources"):

                for source in result["sources"]:

                    with st.container(border=True):

                        st.markdown(
                            f"**📄 {source['filename']}**"
                        )

                        st.caption(
                            f"Entry {source['entry_index']}"
                        )

                        st.write(source["text"])

    messages.append(
        {
            "role": "assistant",
            "content": result["answer"],
            "sources": result["sources"],
        }
    )