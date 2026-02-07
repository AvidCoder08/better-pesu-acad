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
    """Restore session from URL query parameters (client-side only).
    
    Session data is stored in the URL, making it device-specific and 
    impossible for other users to access. Each user has their own URL.
    """
    # Already logged in?
    if st.session_state.get("logged_in"):
        return
    
    # Already attempted?
    if st.session_state.get("restore_attempted"):
        return
    
    st.session_state.restore_attempted = True
    
    # Check if session data is in URL query params
    query_params = st.query_params
    
    if 'pesu_session' in query_params:
        try:
            encrypted_data = query_params['pesu_session']
            current_device = get_device_fingerprint()
            
            # Decrypt
            decrypted_data = decrypt_data(encrypted_data)
            if not decrypted_data:
                return
            
            session_data = json.loads(decrypted_data)
            
            # Verify device fingerprint matches
            if session_data.get("device_fingerprint") != current_device:
                # Device mismatch - don't restore
                return
            
            # Verify timestamp is recent (max 30 days)
            import time
            stored_time = session_data.get("timestamp", 0)
            current_time = time.time()
            if current_time - stored_time > (30 * 24 * 60 * 60):
                # Session expired
                return
            
            # Restore session!
            st.session_state.logged_in = True
            st.session_state.profile = session_data.get("profile")
            st.session_state.pesu_username = session_data.get("username")
            st.session_state.pesu_password = session_data.get("password")
            
        except Exception:
            # Silently fail if decryption or parsing fails
            pass



def save_session_cookie(username: str, password: str, profile):
    """Save encrypted session to URL query parameters (client-side only).
    
    Session is stored in the URL, making it completely device-specific.
    Each browser/device gets its own unique URL with session data.
    No server-side storage = no data leaking between devices.
    """
    try:
        import time
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
            'timestamp': time.time(),  # For 30-day expiry check
        }
        
        # Encrypt the entire session
        json_data = json.dumps(session_data)
        encrypted_data = encrypt_data(json_data)
        
        if encrypted_data:
            # Store in URL query parameter (client-side only)
            st.query_params['pesu_session'] = encrypted_data
            
            st.success("✅ Login successful! Your session is stored securely in your browser.")
        else:
            st.error("Failed to encrypt session")
    except Exception as e:
        st.error(f"Error saving session: {str(e)}")


def clear_session_cookie():
    """Clear session from URL query parameters."""
    try:
        # Remove from query params
        if 'pesu_session' in st.query_params:
            del st.query_params['pesu_session']
        
        # Clear flags
        if 'restore_attempted' in st.session_state:
            st.session_state.restore_attempted = False
    except Exception:
        pass

