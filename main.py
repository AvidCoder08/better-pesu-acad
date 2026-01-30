import streamlit as st
import json
import extra_streamlit_components as stx

st.set_page_config(page_title="Better PESU", page_icon=":books:", layout="wide")

# Initialize cookie manager (stores data in browser)
cookie_manager = stx.CookieManager()

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'profile' not in st.session_state:
    st.session_state.profile = None

# Try to restore session from browser cookies
if not st.session_state.logged_in:
    try:
        session_cookie = cookie_manager.get('pesu_session')
        if session_cookie:
            session_data = json.loads(session_cookie)
            st.session_state.logged_in = True
            st.session_state.profile = session_data.get('profile')
            st.session_state.pesu_username = session_data.get('username')
            st.session_state.pesu_password = session_data.get('password')
    except:
        pass  # Cookie not found or invalid

logo_svg = """
<svg width="300" height="50">
  <text x="0" y="40" font-family="Roboto" font-size="40" fill='#fafafa'>Hail Mary (Beta)</text>
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

pg = st.navigation([page for page in [
    st.Page("login.py", title="Login", icon=":material/login:") if not st.session_state.logged_in else None,
    st.Page("dashboard.py",title="Dashboard",icon=":material/dashboard:"),
    st.Page("courses.py", title="Courses",icon=":material/backpack:"),
    st.Page("marks.py", title="Grades",icon=":material/trophy:"),
    st.Page("settings.py",title="Settings",icon=":material/settings:")
] if page is not None])

pg.run()