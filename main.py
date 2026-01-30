import streamlit as st
import json
import os

st.set_page_config(page_title="Better PESU", page_icon=":books:", layout="wide")

# Load saved session on app startup
SESSION_FILE = ".session_data.json"

def load_session():
    """Load session data from JSON file"""
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, 'r') as f:
                return json.load(f)
        except:
            return None
    return None

# Initialize session state on app load
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'profile' not in st.session_state:
    st.session_state.profile = None

# Restore saved session if it exists
if not st.session_state.logged_in:
    saved_session = load_session()
    if saved_session:
        st.session_state.logged_in = True
        st.session_state.profile = saved_session.get('profile')
        st.session_state.pesu_username = saved_session.get('username')
        st.session_state.pesu_password = saved_session.get('password')

logo_svg = """
<svg width="200" height="50">
  <text x="0" y="40" font-family="Segoe UI Variable Display" font-size="40" fill='#fafafa'>Hail Mary</text>
</svg>
"""
st.logo(logo_svg)
st.markdown("""
<style>
html, body, [class*="css"]  {
  font-family: system-ui, -apple-system, BlinkMacSystemFont,
               "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

</style>
""",unsafe_allow_html=True)


# Show login status in sidebar
if st.session_state.logged_in and st.session_state.profile:
    with st.sidebar:
        st.success("✓ Logged in")
        if isinstance(st.session_state.profile, dict):
            personal = st.session_state.profile.get('personal', {})
            name = personal.get('name', 'User') if isinstance(personal, dict) else personal.get('name', 'User')
            section = personal.get('section', 'N/A') if isinstance(personal, dict) else personal.get('section', 'N/A')
            semester = personal.get('semester', 'N/A') if isinstance(personal, dict) else personal.get('semester', 'N/A')
        else:
            name = st.session_state.profile.personal.name if hasattr(st.session_state.profile, 'personal') else 'User'
            section = st.session_state.profile.personal.section if hasattr(st.session_state.profile, 'personal') else 'N/A'
            semester = st.session_state.profile.personal.semester if hasattr(st.session_state.profile, 'personal') else 'N/A'
        st.caption(f"**{name}**")
        st.caption(f"{section} • Sem {semester}")
        
        st.divider()
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            import os
            SESSION_FILE = ".session_data.json"
            if os.path.exists(SESSION_FILE):
                os.remove(SESSION_FILE)
            st.session_state.logged_in = False
            st.session_state.profile = None
            st.session_state.pesu_username = None
            st.session_state.pesu_password = None
            st.success("Logged out successfully!")
            st.rerun()

pg = st.navigation([
    st.Page("login.py", title="Login", icon=":material/login:"),
    st.Page("dashboard.py",title="Dashboard",icon=":material/dashboard:"),
    st.Page("courses.py", title="Courses",icon=":material/backpack:"),
    st.Page("marks.py", title="Grades",icon=":material/trophy:"),
    st.Page("settings.py",title="Settings",icon=":material/settings:")
])

pg.run()