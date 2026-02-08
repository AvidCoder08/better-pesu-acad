import json
import streamlit as st
import hashlib
import platform
import socket
import os
import base64
import time
import uuid
from extra_streamlit_components import CookieManager
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

COOKIE_NAME = "pesu_session_id"
ENCRYPTION_KEY_FILE = ".session_key"
SESSION_DIR = ".sessions"

# Initialize cookie manager once
_cookie_manager = None

def get_cookie_manager():
    global _cookie_manager
    if _cookie_manager is None:
        _cookie_manager = CookieManager()
    return _cookie_manager


def get_device_fingerprint() -> str:
    """Generate a device fingerprint based on hardware/browser characteristics.
    
    This prevents one user's session from being restored on a different device.
    """
    try:
        machine_name = socket.gethostname()
        system = platform.system()
        processor = platform.processor()
        hw_string = f"{machine_name}:{system}:{processor}"
        device_id = hashlib.sha256(hw_string.encode()).hexdigest()[:16]
        return device_id
    except Exception:
        return "unknown_device"


def get_device_fingerprint() -> str:
    """Generate a device fingerprint for validation.
    
    Note: On Streamlit Cloud, this returns the server's info, so it's only
    used for validation, not for unique identification.
    """
    try:
        machine_name = socket.gethostname()
        system = platform.system()
        processor = platform.processor()
        hw_string = f"{machine_name}:{system}:{processor}"
        device_id = hashlib.sha256(hw_string.encode()).hexdigest()[:16]
        return device_id
    except Exception:
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



def restore_session_from_cookie():
    """Restore Firebase session from cookie + server-side file."""
    if st.session_state.get("authenticated"):
        return

    if st.session_state.get("restore_attempted"):
        return

    st.session_state.restore_attempted = True

    try:
        # Get session ID from cookie
        cookie_manager = get_cookie_manager()
        cookies = cookie_manager.get_all()
        
        if not cookies or COOKIE_NAME not in cookies:
            return
        
        session_id = cookies[COOKIE_NAME]
        if not session_id:
            return
        
        # Create sessions directory if needed
        os.makedirs(SESSION_DIR, exist_ok=True)
        
        # Look for session file
        session_file = os.path.join(SESSION_DIR, f"{session_id}.json")
        if not os.path.exists(session_file):
            return

        # Load and decrypt session data
        with open(session_file, 'r') as f:
            encrypted_data = f.read()

        decrypted_data = decrypt_data(encrypted_data)
        if not decrypted_data:
            if os.path.exists(session_file):
                os.remove(session_file)
            return

        session_data = json.loads(decrypted_data)
        
        # Check expiry (30 days)
        stored_time = session_data.get("timestamp", 0)
        if time.time() - stored_time > (30 * 24 * 60 * 60):
            if os.path.exists(session_file):
                os.remove(session_file)
            return

        # Restore Firebase session to Streamlit state
        st.session_state.authenticated = True
        st.session_state.user_email = session_data.get("user_email")
        st.session_state.user_id = session_data.get("user_id")
        st.session_state.id_token = session_data.get("id_token")
        st.session_state.user_name = session_data.get("user_name")
        st.session_state.user_branch = session_data.get("user_branch")
        st.session_state.current_page = "dashboard"
        
    except Exception as e:
        # Clean up on any error
        try:
            if 'session_file' in locals() and os.path.exists(session_file):
                os.remove(session_file)
        except:
            pass



def save_session_cookie(user_email: str, user_id: str, id_token: str, user_name: str = None, user_branch: str = None):
    """Save encrypted Firebase session to server file + store session ID in cookie.
    
    Args:
        user_email: User's email address
        user_id: Firebase user ID
        id_token: Firebase ID token
        user_name: User's name (optional)
        user_branch: User's branch (optional)
    """
    try:
        # Generate unique session ID
        session_id = str(uuid.uuid4())

        session_data = {
            "user_email": user_email,
            "user_id": user_id,
            "id_token": id_token,
            "user_name": user_name,
            "user_branch": user_branch,
            "timestamp": time.time(),
        }

        # Encrypt and save to file
        json_data = json.dumps(session_data)
        encrypted_data = encrypt_data(json_data)
        if not encrypted_data:
            return False

        # Create sessions directory
        os.makedirs(SESSION_DIR, exist_ok=True)
        
        # Save to file named with session ID
        session_file = os.path.join(SESSION_DIR, f"{session_id}.json")
        with open(session_file, 'w') as f:
            f.write(encrypted_data)
        
        # Store only the session ID in cookie
        cookie_manager = get_cookie_manager()
        cookie_manager.set(COOKIE_NAME, session_id, max_age=30 * 24 * 60 * 60)
        
        return True
        
    except Exception as e:
        return False


def clear_session_cookie():
    """Clear session cookie and delete server-side file."""
    try:
        # Get session ID from cookie
        cookie_manager = get_cookie_manager()
        cookies = cookie_manager.get_all()
        
        if cookies and COOKIE_NAME in cookies:
            session_id = cookies[COOKIE_NAME]
            
            # Delete session file
            session_file = os.path.join(SESSION_DIR, f"{session_id}.json")
            if os.path.exists(session_file):
                os.remove(session_file)
        
        # Delete cookie
        cookie_manager.delete(COOKIE_NAME)
        
        if "restore_attempted" in st.session_state:
            st.session_state.restore_attempted = False
            
    except Exception:
        pass

