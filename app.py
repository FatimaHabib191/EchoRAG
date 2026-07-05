import streamlit as st

from views.auth_page import show_auth_page
from views.dashboard import show_dashboard


st.set_page_config(
    page_title="Roast My Past Self",
    page_icon="🧠",
    layout="wide",
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None


if st.session_state.logged_in:

    show_dashboard()

else:

    show_auth_page()