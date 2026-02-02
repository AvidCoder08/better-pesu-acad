import json
import streamlit as st
import extra_streamlit_components as stx
import hashlib
import platform
import socket

COOKIE_NAME = "pesu_session"
COOKIE_MANAGER_KEY = "pesu_cookie_manager"


def get_device_fingerprint() -> str:
    """Generate a device fingerprint based on hardware/browser characteristics.
    
    This prevents one user's session from being restored on a different device,
    similar to CineBase's security approach.
    """
    try:
        machine_name = socket.gethostname()
        system = platform.system()
        processor = platform.processor()
        hw_string = f"{machine_name}:{system}:{processor}"
        device_id = hashlib.sha256(hw_string.encode()).hexdigest()[:16]
        return device_id
    except Exception:
        # Fallback if device fingerprinting fails
        return "unknown_device"


def get_cookie_manager():
    """Get or create cookie manager instance stored in session state."""
    if "cookie_manager" not in st.session_state:
        st.session_state.cookie_manager = stx.CookieManager(key=COOKIE_MANAGER_KEY)
    return st.session_state.cookie_manager


def restore_session_from_cookie():
    """Restore session state from browser cookie if available.
    
    Only restores if device fingerprint matches to prevent one user's profile
    from being visible on another device.
    """
    if st.session_state.get("logged_in"):
        return

    try:
        current_device = get_device_fingerprint()
        cookie_manager = get_cookie_manager()
        session_cookie = cookie_manager.get(COOKIE_NAME)
        
        if session_cookie:
            try:
                session_data = json.loads(session_cookie)
            except json.JSONDecodeError:
                # Cookie is corrupted, clear it
                clear_session_cookie()
                return
            
            # Security check: verify device fingerprint matches
            stored_device = session_data.get("device_fingerprint")
            
            # If no stored device or devices match, restore the session
            if stored_device and stored_device != current_device:
                # Device mismatch - clear the session for security
                clear_session_cookie()
                return
            
            # Restore session
            st.session_state.logged_in = True
            st.session_state.profile = session_data.get("profile")
            st.session_state.pesu_username = session_data.get("username")
            st.session_state.pesu_password = session_data.get("password")
    except Exception as e:
        # Silently fail but don't break the app
        pass


def save_session_cookie(username: str, password: str, profile):
    """Save session to browser cookie with device fingerprint for security."""
    cookie_manager = get_cookie_manager()
    
    # Convert profile to dict
    if hasattr(profile, 'model_dump'):
        profile_dict = profile.model_dump()
    elif hasattr(profile, 'dict'):
        profile_dict = profile.dict()
    elif isinstance(profile, dict):
        profile_dict = profile
    else:
        profile_dict = profile.__dict__ if hasattr(profile, '__dict__') else {}
    
    session_data = {
        'username': username,
        'password': password,
        'profile': profile_dict,
        'device_fingerprint': get_device_fingerprint(),  # Add device fingerprint
    }
    
    # Save to browser cookie (expires in 30 days)
    cookie_manager.set('pesu_session', json.dumps(session_data), max_age=30*24*60*60)


def clear_session_cookie():
    """Clear session cookie."""
    try:
        cookie_manager = get_cookie_manager()
        cookie_manager.delete('pesu_session')
    except Exception:
        pass

