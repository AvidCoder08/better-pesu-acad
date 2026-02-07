import streamlit as st
from dotenv import load_dotenv
from session_utils import restore_session_from_cookie
from role_utils import is_superadmin, is_cr

load_dotenv()

st.set_page_config(page_title="Better PESU", page_icon=":school:", layout="wide")

# Initialize session state BEFORE restoring from cookie
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'profile' not in st.session_state:
    st.session_state.profile = None
if 'pesu_username' not in st.session_state:
    st.session_state.pesu_username = None
if 'pesu_password' not in st.session_state:
    st.session_state.pesu_password = None
if 'restore_attempted' not in st.session_state:
    st.session_state.restore_attempted = False

# Try to restore session from browser cookies
restore_session_from_cookie()

logo_svg = """
<svg width="450" height="50">
  <text x="0" y="40" font-family="Roboto" font-size="40" fill='#fafafa'>Better PESU Acad (Beta)</text>
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
        st.caption(f"{section} • {semester}")
else:
    # Hide sidebar on login page
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)

profile = st.session_state.profile

pg = st.navigation([page for page in [
    st.Page("login.py", title="Login", icon="🔐") if not st.session_state.logged_in else None,
    st.Page("dashboard.py", title="Dashboard", icon="🏠"),
    st.Page("courses.py", title="Courses", icon="📚"),
    st.Page("timetable.py", title="Schedule", icon="📅"),
    st.Page("attendance.py", title="Attendance", icon="✅"),
    #st.Page("marks.py", title="Grades", icon="🏆"),
    st.Page("exam_seating.py", title="Exam Seating", icon="📍"),
    st.Page("campusmap.py", title="Campus Map", icon="🗺️"),
    st.Page("admin.py", title="Class Admin", icon="👩‍💼") if st.session_state.logged_in and profile and is_cr(profile) else None,
    st.Page("superadmin.py", title="Superadmin", icon="🧑‍💻") if st.session_state.logged_in and profile and is_superadmin(profile) else None,
    st.Page("settings.py", title="Settings", icon="⚙️")
] if page is not None])

pg.run()