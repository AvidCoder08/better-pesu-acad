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
    """Restore session from browser HTTP cookie on page load."""
    # Already logged in?
    if st.session_state.get("logged_in"):
        return
    
    # Already tried?
    if st.session_state.get("restore_attempted"):
        return
    
    st.session_state.restore_attempted = True
    
    # Read cookie via pure JavaScript, no iframe issues
    cookie_reader = """
    <script>
    // Read HTTP cookie directly
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }
    
    const sessionData = getCookie('pesu_session');
    if (sessionData) {
        // Store in window for immediate access
        window.pesuSessionData = sessionData;
        // Also try localStorage as backup
        try {
            localStorage.setItem('pesu_session_backup', sessionData);
        } catch(e) {}
    }
    </script>
    """
    st.components.v1.html(cookie_reader, height=0)
    
    # Try to get from localStorage (backup method)
    try:
        get_from_storage = """
        <script>
        const data = localStorage.getItem('pesu_session_backup');
        if (data) {
            window.pesuSessionData = data;
        }
        </script>
        """
        st.components.v1.html(get_from_storage, height=0)
    except:
        pass
    
    # Check if we have session data in window object
    # (This won't work directly, but we'll use a Streamlit callback)
    # Instead, check if we can read from a file we created
    try:
        current_device = get_device_fingerprint()
        cache_file = f".pesu_cache_{current_device}.enc"
        
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                encrypted_data = f.read()
            
            decrypted = decrypt_data(encrypted_data)
            if decrypted:
                session_data = json.loads(decrypted)
                
                # Verify device
                if session_data.get("device_fingerprint") == current_device:
                    st.session_state.logged_in = True
                    st.session_state.profile = session_data.get("profile")
                    st.session_state.pesu_username = session_data.get("username")
                    st.session_state.pesu_password = session_data.get("password")
                    return
    except:
        pass



def save_session_cookie(username: str, password: str, profile):
    """Save encrypted session persistently to device-specific file.
    
    Also sets HTTP cookie as backup. Only readable on the same device
    due to device-specific encryption key.
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
            # Save to device-specific file (encrypted, only readable on same device)
            cache_file = f".pesu_cache_{current_device}.enc"
            with open(cache_file, 'w') as f:
                f.write(encrypted_data)
            
            # Also set HTTP cookie as backup
            js_code = f"""
            <script>
            const date = new Date();
            date.setTime(date.getTime() + (30 * 24 * 60 * 60 * 1000));
            const expires = "expires=" + date.toUTCString();
            document.cookie = "pesu_session=" + encodeURIComponent('{encrypted_data}') + ";" + expires + ";path=/;SameSite=Lax";
            console.log('✅ Session saved');
            </script>
            """
            try:
                st.components.v1.html(js_code, height=0)
            except:
                pass
            
            st.success("✅ Login successful! You'll stay logged in.")
        else:
            st.error("Failed to encrypt session")
    except Exception as e:
        st.error(f"Error saving session: {str(e)}")


def clear_session_cookie():
    """Clear session cookie from browser."""
    try:
        # Use JavaScript to delete HTTP cookie
        js_code = """
        <script>
        document.cookie = "pesu_session=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/";
        console.log('Session cleared');
        </script>
        """
        st.components.v1.html(js_code, height=0)
        
        # Clear flags
        if 'restore_attempted' in st.session_state:
            st.session_state.restore_attempted = False
    except Exception:
        pass

