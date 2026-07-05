import streamlit as st

from auth.database import SessionLocal
from auth.auth_service import AuthService


def show_auth_page():

    st.title("EchoRAG")


    st.caption(
        "Your memories, intelligently retrieved."
    )

    login_tab, register_tab = st.tabs(
        ["Login", "Register"]
    )

    db = SessionLocal()

    with login_tab:

        st.subheader("Login")

        username = st.text_input(
            "Username",
            key="login_username"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "Login",
            use_container_width=True
        ):

            user = AuthService.authenticate(
                db,
                username,
                password
            )

            if user:

                st.session_state.logged_in = True
                st.session_state.user = user

                st.success("Login successful!")

                st.rerun()

            else:

                st.error(
                    "Invalid username or password."
                )

    with register_tab:

        st.subheader("Register")

        username = st.text_input(
            "Username",
            key="register_username"
        )

        email = st.text_input(
            "Email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="register_password"
        )

        confirm = st.text_input(
            "Confirm Password",
            type="password"
        )

        if st.button(
            "Create Account",
            use_container_width=True
        ):

            if password != confirm:

                st.error(
                    "Passwords do not match."
                )

            else:

                try:

                    AuthService.create_user(
                        db,
                        username,
                        email,
                        password
                    )

                    st.success(
                        "Account created successfully!"
                    )

                except Exception as e:

                    st.error(str(e))

    db.close()