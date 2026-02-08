import json
import streamlit as st
import streamlit.components.v1 as components
import hashlib
import platform
import socket
import os
import base64
import time
import uuid
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

COOKIE_NAME = "pesu_session_id"
ENCRYPTION_KEY_FILE = ".session_key"
SESSION_DIR = ".sessions"


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


def get_encryption_key() -> bytes:
    """Get or generate encryption key for cookie data.
    
    The key is stored locally and tied to this device, ensuring cookies
    are encrypted and can only be decrypted on the same machine.
    """
    if os.path.exists(ENCRYPTION_KEY_FILE):
        with open(ENCRYPTION_KEY_FILE, 'rb') as f:
            return f.read()
    else:
        # Generate new key based on device fingerprint
        device_fp = get_device_fingerprint()
        salt = b'pesu_session_salt_v1'  # Static salt for key derivation
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(device_fp.encode()))
        
        # Save key to file
        with open(ENCRYPTION_KEY_FILE, 'wb') as f:
            f.write(key)
        
        return key


def encrypt_data(data: str) -> str:
    """Encrypt session data before storing in cookie."""
    try:
        key = get_encryption_key()
        fernet = Fernet(key)
        encrypted = fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    except Exception:
        return None


def decrypt_data(encrypted_data: str) -> str:
    """Decrypt session data from cookie."""
    try:
        key = get_encryption_key()
        fernet = Fernet(key)
        decoded = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted = fernet.decrypt(decoded)
        return decrypted.decode()
    except Exception:
        return None



def _get_cookie(cookie_name: str):
    """Get a cookie using HTML/JS component."""
    html_code = f"""
    <script>
    function getCookie(name) {{
        const value = `; ${{document.cookie}}`;
        const parts = value.split(`; ${{name}}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }}
    const cookie_value = getCookie("{cookie_name}");
    window.parent.postMessage({{cookie: cookie_value}}, "*");
    </script>
    """
    result = components.html(html_code, height=0)
    return result


def _set_cookie(cookie_name: str, value: str, days: int = 30):
    """Set a cookie using HTML/JS component."""
    html_code = f"""
    <script>
    const expires = new Date(Date.now() + {days * 24 * 60 * 60 * 1000}).toUTCString();
    document.cookie = "{cookie_name}=" + "{value}" + "; expires=" + expires + "; path=/; SameSite=Lax";
    </script>
    """
    components.html(html_code, height=0)


def _delete_cookie(cookie_name: str):
    """Delete a cookie using HTML/JS component."""
    html_code = f"""
    <script>
    document.cookie = "{cookie_name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    </script>
    """
    components.html(html_code, height=0)


def restore_session_from_cookie():
    """Restore session from browser cookie + server-side session file."""
    if st.session_state.get("logged_in"):
        return

    if st.session_state.get("restore_attempted"):
        return

    st.session_state.restore_attempted = True

    # Get session ID from cookie
    session_id = _get_cookie(COOKIE_NAME)
    if not session_id or not isinstance(session_id, dict):
        return
    
    session_id = session_id.get("cookie")
    if not session_id:
        return

    # Create sessions directory if it doesn't exist
    os.makedirs(SESSION_DIR, exist_ok=True)
    
    # Load session data from file
    session_file = os.path.join(SESSION_DIR, f"{session_id}.json")
    if not os.path.exists(session_file):
        return

    try:
        with open(session_file, 'r') as f:
            encrypted_data = f.read()

        current_device = get_device_fingerprint()
        decrypted_data = decrypt_data(encrypted_data)
        if not decrypted_data:
            return

        session_data = json.loads(decrypted_data)
        
        # Verify device fingerprint
        if session_data.get("device_fingerprint") != current_device:
            # Session from different device - delete it
            os.remove(session_file)
            return

        # Check expiry (30 days)
        stored_time = session_data.get("timestamp", 0)
        if time.time() - stored_time > (30 * 24 * 60 * 60):
            os.remove(session_file)
            return

        # Restore session
        st.session_state.logged_in = True
        st.session_state.profile = session_data.get("profile")
        st.session_state.pesu_username = session_data.get("username")
        st.session_state.pesu_password = session_data.get("password")
    except Exception:
        # Clean up bad session file
        if os.path.exists(session_file):
            os.remove(session_file)



def save_session_cookie(username: str, password: str, profile):
    """Save encrypted session to server file + set cookie with session ID."""
    try:
        current_device = get_device_fingerprint()

        # Generate unique session ID
        session_id = str(uuid.uuid4())

        # Prepare session data
        if hasattr(profile, "model_dump"):
            profile_dict = profile.model_dump()
        elif hasattr(profile, "dict"):
            profile_dict = profile.dict()
        elif isinstance(profile, dict):
            profile_dict = profile
        else:
            profile_dict = profile.__dict__ if hasattr(profile, "__dict__") else {}

        session_data = {
            "username": username,
            "password": password,
            "profile": profile_dict,
            "device_fingerprint": current_device,
            "timestamp": time.time(),
        }

        # Encrypt and save to file
        json_data = json.dumps(session_data)
        encrypted_data = encrypt_data(json_data)
        if not encrypted_data:
            st.error("Failed to encrypt session")
            return

        # Create sessions directory
        os.makedirs(SESSION_DIR, exist_ok=True)
        
        # Save to file
        session_file = os.path.join(SESSION_DIR, f"{session_id}.json")
        with open(session_file, 'w') as f:
            f.write(encrypted_data)

        # Set cookie with session ID (small string, won't cause 414)
        _set_cookie(COOKIE_NAME, session_id, days=30)
        
    except Exception as e:
        st.error(f"Error saving session: {str(e)}")


def clear_session_cookie():
    """Clear session cookie and delete session file."""
    try:
        # Get session ID from cookie first
        session_id = _get_cookie(COOKIE_NAME)
        if session_id and isinstance(session_id, dict):
            session_id = session_id.get("cookie")
            if session_id:
                # Delete session file
                session_file = os.path.join(SESSION_DIR, f"{session_id}.json")
                if os.path.exists(session_file):
                    os.remove(session_file)
        
        # Delete cookie
        _delete_cookie(COOKIE_NAME)
        
        if "restore_attempted" in st.session_state:
            st.session_state.restore_attempted = False
    except Exception:
        pass

