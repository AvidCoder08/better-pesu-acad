import streamlit as st
import asyncio
import json
import os
from pesuacademy import PESUAcademy

# Session file path
SESSION_FILE = ".session_data.json"

def save_session(username, password, profile):
    """Save session data to a JSON file"""
    session_data = {
        "username": username,
        "password": password,
        "profile": profile.model_dump() if hasattr(profile, 'model_dump') else profile.dict()
    }
    with open(SESSION_FILE, 'w') as f:
        json.dump(session_data, f)

def load_session():
    """Load session data from JSON file"""
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, 'r') as f:
                return json.load(f)
        except:
            return None
    return None

def clear_session():
    """Clear saved session data"""
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

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
