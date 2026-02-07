import json
import streamlit as st
import extra_streamlit_components as stx
import hashlib
import platform
import socket
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

COOKIE_NAME = "pesu_session"
COOKIE_MANAGER_KEY = "pesu_cookie_manager"
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



def get_cookie_manager():
    """Get or create cookie manager instance."""
    if "cookie_manager" not in st.session_state:
        st.session_state.cookie_manager = stx.CookieManager()
    return st.session_state.cookie_manager


def restore_session_from_cookie():
    """Restore session state from browser cookie if available.
    
    Only restores if device fingerprint matches to prevent one user's profile
    from being visible on another device. Decrypts encrypted cookie data.
    """
    # Skip if already logged in or already attempted restore
    if st.session_state.get("logged_in") or st.session_state.get("restore_attempted"):
        return
    
    # Mark that we've attempted restore (prevents multiple attempts)
    st.session_state.restore_attempted = True

    try:
        current_device = get_device_fingerprint()
        cookie_manager = get_cookie_manager()
        
        # Get all cookies - this returns empty dict if not ready yet
        all_cookies = cookie_manager.get_all()
        
        # If cookies aren't ready yet or no session cookie exists
        if not all_cookies or COOKIE_NAME not in all_cookies:
            return
        
        encrypted_cookie = all_cookies[COOKIE_NAME]
        
        if encrypted_cookie:
            # Decrypt the cookie data
            decrypted_data = decrypt_data(encrypted_cookie)
            if not decrypted_data:
                # Decryption failed, clear cookie
                clear_session_cookie()
                return
            
            try:
                session_data = json.loads(decrypted_data)
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
    """Save session to browser cookie with encryption and device fingerprint for security."""
    try:
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
            'device_fingerprint': get_device_fingerprint(),
        }
        
        # Encrypt the session data before saving
        json_data = json.dumps(session_data)
        encrypted_data = encrypt_data(json_data)
        
        if encrypted_data:
            # Save encrypted data to browser cookie (expires in 30 days)
            cookie_manager.set(COOKIE_NAME, encrypted_data, max_age=30*24*60*60)
    except Exception as e:
        # If cookie save fails, continue anyway (user will just need to login again)
        pass


def clear_session_cookie():
    """Clear session cookie and reset restore flag."""
    try:
        cookie_manager = get_cookie_manager()
        cookie_manager.delete(COOKIE_NAME)
        if 'restore_attempted' in st.session_state:
            st.session_state.restore_attempted = False
    except Exception:
        pass

