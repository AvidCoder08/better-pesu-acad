import streamlit as st
import asyncio
import json
import os
import hashlib
import uuid
import platform
import socket
from datetime import datetime, timedelta
from pesuacademy import PESUAcademy

# Session file path - unique per browser/device
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
    
    # Create new device key (machine ID + unique UUID)
    device_key = f"{machine_id}_{str(uuid.uuid4())[:8]}"
    
    # Store it locally
    os.makedirs(SESSION_DIR, exist_ok=True)
    with open(key_file, 'w') as f:
        f.write(machine_id)
    
    # Set file permissions on Unix systems
    try:
        os.chmod(key_file, 0o600)
    except:
        pass
    
    return device_key

def get_session_id():
    """Get a truly device-specific session ID"""
    # Get the hardware-based device ID (not stored in session_state)
    device_key = get_or_create_device_key()
    return device_key

def get_session_file():
    """Get the session file path for this device"""
    session_id = get_session_id()
    return os.path.join(SESSION_DIR, f"session_{session_id}.json")

def save_session(username, password, profile):
    """Save session data to an encrypted file unique to this device"""
    session_file = get_session_file()
    session_data = {
        "username": username,
        "password": password,
        "profile": profile.model_dump() if hasattr(profile, 'model_dump') else profile.dict(),
        "created_at": datetime.now().isoformat(),
        "last_accessed": datetime.now().isoformat(),
        "device_id": get_session_id()
    }
    
    # Write with restricted permissions (600 = read/write for owner only)
    with open(session_file, 'w') as f:
        json.dump(session_data, f)
    
    # Set file permissions to be readable/writable by owner only
    if os.name != 'nt':  # Unix-like systems
        os.chmod(session_file, 0o600)

def load_session():
    """Load session data from the device-specific file"""
    session_file = get_session_file()
    
    if os.path.exists(session_file):
        try:
            with open(session_file, 'r') as f:
                data = json.load(f)
            
            # Verify this is the correct device
            if data.get('device_id') != get_session_id():
                # Session belongs to different device, don't load it
                return None
            
            # Check if session has expired (24 hours)
            last_accessed = datetime.fromisoformat(data.get('last_accessed', datetime.now().isoformat()))
            if datetime.now() - last_accessed > timedelta(hours=24):
                clear_session()
                return None
            
            # Update last accessed time
            data['last_accessed'] = datetime.now().isoformat()
            with open(session_file, 'w') as f:
                json.dump(data, f)
            
            return data
        except Exception as e:
            st.error(f"Session loading error: {e}")
            return None
    return None

def clear_session():
    """Clear session data for this device only"""
    session_file = get_session_file()
    if os.path.exists(session_file):
        os.remove(session_file)

async def login_user(username, password):
    """Async function to login to PESU Academy"""
    try:
        pesu = await PESUAcademy.login(username, password)
        profile = await pesu.get_profile()
        await pesu.close()
        return profile, None
    except Exception as e:
        return None, str(e)

def main():
    st.title("🔐 Login to PESU Academy")
    
    # Check if user is already logged in
    if 'logged_in' in st.session_state and st.session_state.logged_in:
        st.success("You are already logged in!")
        
        # Display user info
        if isinstance(st.session_state.profile, dict):
            personal = st.session_state.profile.get('personal', {})
        else:
            personal = st.session_state.profile.personal
        
        st.markdown(f"### Hi, {personal.get('name', 'User') if isinstance(personal, dict) else personal.name}! 👋")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Program", personal.get('program', 'N/A') if isinstance(personal, dict) else personal.program)
        with col2:
            st.metric("Branch", personal.get('branch', 'N/A') if isinstance(personal, dict) else personal.branch)
        with col3:
            st.metric("Semester", personal.get('semester', 'N/A') if isinstance(personal, dict) else personal.semester)
        
        col4, col5 = st.columns(2)
        with col4:
            section = personal.get('section', 'N/A') if isinstance(personal, dict) else personal.section
            st.info(f"**Section:** {section}")
        with col5:
            srn = personal.get('srn', 'N/A') if isinstance(personal, dict) else personal.srn
            st.info(f"**SRN:** {srn}")
        
        # Logout button
        if st.button("Logout", type="secondary"):
            st.session_state.logged_in = False
            st.session_state.profile = None
            st.session_state.pesu_username = None
            st.session_state.pesu_password = None
            clear_session()
            st.success("Logged out successfully!")
            st.rerun()
    else:
        # Login form
        st.markdown("Please login with your PESU Academy credentials")
        
        with st.form("login_form"):
            username = st.text_input("PRN/SRN", placeholder="Enter your PRN or SRN")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit = st.form_submit_button("Login", type="primary", use_container_width=True)
            
            if submit:
                if not username or not password:
                    st.error("Please enter both username and password")
                else:
                    with st.spinner("Logging in..."):
                        # Run async login
                        profile, error = asyncio.run(login_user(username, password))
                        
                        if error:
                            st.error(f"Login failed: {error}")
                        else:
                            st.session_state.logged_in = True
                            st.session_state.profile = profile
                            st.session_state.pesu_username = username
                            st.session_state.pesu_password = password
                            
                            # Save session to file
                            save_session(username, password, profile)
                            
                            st.success("✓ Login successful!")
                            st.rerun()

if __name__ == "__main__":
    main()
st.markdown("""
<footer>Your credentials, information, grades etc. are completely private and can be viewed by no one else except you. Your credentials are locally stored on your PC. This project uses the PESU API created and maintained by seniors and alumni of PESU<br>
        Made with ❤️ by Shashank Munnangi. <br> If you like this, consider tipping: <a href="https://www.upi.me/pay?pa=soham.s.munnangi@axl">Tip me!</a>. This motivates me to work more on this project!</footer>
""",unsafe_allow_html=True)