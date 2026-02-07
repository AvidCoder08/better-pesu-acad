import json
import streamlit as st
import hashlib
import platform
import socket
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

COOKIE_NAME = "pesu_session"
ENCRYPTION_KEY_FILE = ".session_key"
SESSION_STORAGE_DIR = ".session_data"


def ensure_session_dir():
    """Ensure session storage directory exists."""
    if not os.path.exists(SESSION_STORAGE_DIR):
        os.makedirs(SESSION_STORAGE_DIR, exist_ok=True)


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



def restore_session_from_cookie():
    """Restore session state from encrypted local session file.
    
    Only restores if device fingerprint matches to prevent one user's session
    from being used on a different device.
    """
    # Skip if already logged in or already attempted restore
    if st.session_state.get("logged_in") or st.session_state.get("restore_attempted"):
        return
    
    # Mark that we've attempted restore
    st.session_state.restore_attempted = True
    
    try:
        ensure_session_dir()
        current_device = get_device_fingerprint()
        session_file = os.path.join(SESSION_STORAGE_DIR, f"{current_device}.json.enc")
        
        if not os.path.exists(session_file):
            return
        
        # Read encrypted session data from file
        with open(session_file, 'r') as f:
            encrypted_data = f.read()
        
        # Decrypt the data
        decrypted_data = decrypt_data(encrypted_data)
        if not decrypted_data:
            # Decryption failed, delete the corrupt file
            os.remove(session_file)
            return
        
        session_data = json.loads(decrypted_data)
        
        # Verify device fingerprint matches
        stored_device = session_data.get("device_fingerprint")
        if stored_device != current_device:
            # Device mismatch - shouldn't happen but clear for safety
            os.remove(session_file)
            return
        
        # Restore session
        st.session_state.logged_in = True
        st.session_state.profile = session_data.get("profile")
        st.session_state.pesu_username = session_data.get("username")
        st.session_state.pesu_password = session_data.get("password")
        st.write("🔐 Welcome back! Session restored.") 
    except Exception as e:
        # Silently fail
        pass




def save_session_cookie(username: str, password: str, profile):
    """Save encrypted session to local file for persistence across browser reloads."""
    try:
        ensure_session_dir()
        current_device = get_device_fingerprint()
        
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
            'device_fingerprint': current_device,
        }
        
        # Encrypt the session data
        json_data = json.dumps(session_data)
        encrypted_data = encrypt_data(json_data)
        
        if encrypted_data:
            # Save to local file (encrypted)
            session_file = os.path.join(SESSION_STORAGE_DIR, f"{current_device}.json.enc")
            with open(session_file, 'w') as f:
                f.write(encrypted_data)
            
            st.success("✅ Login successful! You'll stay logged in next time.")
        else:
            st.error("Failed to encrypt session")
    except Exception as e:
        st.error(f"Error saving session: {str(e)}")


def clear_session_cookie():
    """Clear session file and reset restore flag."""
    try:
        ensure_session_dir()
        current_device = get_device_fingerprint()
        session_file = os.path.join(SESSION_STORAGE_DIR, f"{current_device}.json.enc")
        
        if os.path.exists(session_file):
            os.remove(session_file)
        
        if 'restore_attempted' in st.session_state:
            st.session_state.restore_attempted = False
        if 'session_cookie_data' in st.session_state:
            del st.session_state.session_cookie_data
    except Exception:
        pass

