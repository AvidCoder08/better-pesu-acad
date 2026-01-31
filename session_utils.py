import json
import streamlit as st
import extra_streamlit_components as stx

COOKIE_NAME = "pesu_session"
COOKIE_MANAGER_KEY = "pesu_cookie_manager"


def get_cookie_manager():
    """Get or create cookie manager instance stored in session state."""
    if "cookie_manager" not in st.session_state:
        st.session_state.cookie_manager = stx.CookieManager(key=COOKIE_MANAGER_KEY)
    return st.session_state.cookie_manager


def restore_session_from_cookie():
    """Restore session state from browser cookie if available."""
    if st.session_state.get("logged_in"):
        return

    try:
        cookie_manager = get_cookie_manager()
        session_cookie = cookie_manager.get(COOKIE_NAME)
        if session_cookie:
            session_data = json.loads(session_cookie)
            st.session_state.logged_in = True
            st.session_state.profile = session_data.get("profile")
            st.session_state.pesu_username = session_data.get("username")
            st.session_state.pesu_password = session_data.get("password")
    except Exception:
        pass
