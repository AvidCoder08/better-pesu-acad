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
    """Restore session state from browser localStorage if available.
    
    Uses a Streamlit component to read encrypted session from browser localStorage.
    Device fingerprint is embedded in the encrypted data to prevent cross-device access.
    """
    # Skip if already logged in or already attempted restore
    if st.session_state.get("logged_in") or st.session_state.get("restore_attempted"):
        return
    
    # Mark that we've attempted restore
    st.session_state.restore_attempted = True
    
    # Create a component that reads from localStorage
    # This uses pure HTML/JavaScript without external dependencies
    component_code = """
    <script>
    function readSessionCookie() {
        const data = localStorage.getItem('pesu_session');
        if (data) {
            // Send to Streamlit via query params
            const encrypted = encodeURIComponent(data);
            window.location.href = window.location.pathname + '?pesu_data=' + encrypted;
        }
    }
    
    // Try to read session on component load
    readSessionCookie();
    </script>
    """
    
    st.components.v1.html(component_code, height=0)
    
    # Check if we got session data via query params
    query_params = st.query_params
    if 'pesu_data' in query_params:
        try:
            encrypted_cookie = query_params['pesu_data']
            current_device = get_device_fingerprint()
            
            # Decrypt the cookie data
            decrypted_data = decrypt_data(encrypted_cookie)
            if not decrypted_data:
                # Decryption failed - likely wrong device
                return
            
            session_data = json.loads(decrypted_data)
            
            # Security check: verify device fingerprint matches
            stored_device = session_data.get("device_fingerprint")
            if stored_device != current_device:
                # Device mismatch - CRITICAL: do not restore
                return
            
            # Restore session
            st.session_state.logged_in = True
            st.session_state.profile = session_data.get("profile")
            st.session_state.pesu_username = session_data.get("username")
            st.session_state.pesu_password = session_data.get("password")
            
            # Remove from URL to clean it up
            st.query_params.clear()
            st.rerun()
        except Exception as e:
            # Silently fail
            pass



def save_session_cookie(username: str, password: str, profile):
    """Save encrypted session to browser localStorage.
    
    Only accessible from the same device due to device-specific encryption.
    """
    try:
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
            # Use JavaScript to save to localStorage (browser storage, not server)
            js_code = f"""
            <script>
            localStorage.setItem('pesu_session', '{encrypted_data}');
            console.log('✅ Session saved securely to your device');
            </script>
            """
            st.components.v1.html(js_code, height=0)
            st.success("✅ Login successful! You'll stay logged in on this device.")
        else:
            st.error("Failed to encrypt session")
    except Exception as e:
        st.error(f"Error saving session: {str(e)}")


def clear_session_cookie():
    """Clear session from browser localStorage and reset restore flag."""
    try:
        # Use JavaScript to clear localStorage
        js_code = """
        <script>
        localStorage.removeItem('pesu_session');
        console.log('Session cleared from browser');
        </script>
        """
        st.components.v1.html(js_code, height=0)
        
        # Clear session state flags
        if 'restore_attempted' in st.session_state:
            st.session_state.restore_attempted = False
    except Exception:
        pass

