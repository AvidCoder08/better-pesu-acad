import streamlit as st
import json
import os
import hashlib
import platform
import socket
from datetime import datetime

st.set_page_config(page_title="Better PESU", page_icon=":books:", layout="wide")

# Session management - ensure unique session per device
SESSION_DIR = ".sessions"
os.makedirs(SESSION_DIR, exist_ok=True)

def get_machine_id():
    """Generate a hardware-based machine ID that can't be spoofed"""
    try:
        # Combine multiple machine-specific identifiers
        machine_name = socket.gethostname()
        system = platform.system()
        processor = platform.processor()
        
        # Create a hash from hardware identifiers
        hw_string = f"{machine_name}:{system}:{processor}"
        machine_id = hashlib.sha256(hw_string.encode()).hexdigest()[:16]
        return machine_id
    except:
        return None

def get_device_key_file():
    """Get the path to the device key file stored locally"""
    return os.path.join(SESSION_DIR, ".device_key")

def get_or_create_device_key():
    """Get existing device key or create a new one"""
    import uuid
    key_file = get_device_key_file()
    machine_id = get_machine_id()
    
    if not machine_id:
        # Fallback to UUID if machine ID fails
        machine_id = str(uuid.uuid4())
    
    # Check if device key exists and matches this machine
    if os.path.exists(key_file):
        try:
            with open(key_file, 'r') as f:
                stored_id = f.read().strip()
            # Verify it matches current machine
            if stored_id == machine_id:
                return stored_id
        except:
            pass
    
    # Store machine ID locally
    os.makedirs(SESSION_DIR, exist_ok=True)
    with open(key_file, 'w') as f:
        f.write(machine_id)
    
    # Set file permissions on Unix systems
    try:
        os.chmod(key_file, 0o600)
    except:
        pass
    
    return machine_id

def get_session_id():
    """Get a truly device-specific session ID based on hardware"""
    device_key = get_or_create_device_key()
    return device_key

def load_session():
    """Load session data from device-specific file"""
    session_id = get_session_id()
    session_file = os.path.join(SESSION_DIR, f"session_{session_id}.json")
    
    if os.path.exists(session_file):
        try:
            with open(session_file, 'r') as f:
                return json.load(f)
        except:
            return None
    return None

# Initialize session state on app load
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'profile' not in st.session_state:
    st.session_state.profile = None

# Restore saved session if it exists (only for this device)
if not st.session_state.logged_in:
    saved_session = load_session()
    if saved_session:
        st.session_state.logged_in = True
        st.session_state.profile = saved_session.get('profile')
        st.session_state.pesu_username = saved_session.get('username')
        st.session_state.pesu_password = saved_session.get('password')

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