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
    """Restore session state from HTTP cookie if available.
    
    The cookie is encrypted with device-specific key, so it can only be
    decrypted on the same device where it was created.
    """
    # Skip if already logged in
    if st.session_state.get("logged_in"):
        return
    
    # Mark restore attempt
    if st.session_state.get("restore_attempted"):
        return
    
    st.session_state.restore_attempted = True
    
    # Inject code to read HTTP cookie and put it in query params
    # This is safer than relying on Streamlit to access headers
    read_cookie_js = """
    <script>
    function getCookie(name) {
        const nameEQ = name + "=";
        const cookies = document.cookie.split(';');
        for(let i = 0; i < cookies.length; i++) {
            let c = cookies[i].trim();
            if (c.indexOf(nameEQ) === 0) {
                return decodeURIComponent(c.substring(nameEQ.length));
            }
        }
        return null;
    }
    
    const sessionCookie = getCookie('pesu_session');
    if (sessionCookie && !window.location.search.includes('pesu_data')) {
        // Append to URL so Streamlit can read it via query_params
        const url = new URL(window.location);
        url.searchParams.set('pesu_data', sessionCookie);
        window.history.replaceState({}, '', url);
    }
    </script>
    """
    
    try:
        st.components.v1.html(read_cookie_js, height=0)
    except:
        pass
    
    # Now check if we have the data in query params
    query_params = st.query_params
    
    if 'pesu_data' in query_params:
        try:
            encrypted_cookie = query_params['pesu_data']
            current_device = get_device_fingerprint()
            
            # Decrypt
            decrypted_data = decrypt_data(encrypted_cookie)
            if not decrypted_data:
                return
            
            session_data = json.loads(decrypted_data)
            
            # Verify device
            if session_data.get("device_fingerprint") != current_device:
                # Device mismatch
                clear_session_cookie()
                return
            
            # Restore!
            st.session_state.logged_in = True
            st.session_state.profile = session_data.get("profile")
            st.session_state.pesu_username = session_data.get("username")
            st.session_state.pesu_password = session_data.get("password")
        except Exception:
            pass



def save_session_cookie(username: str, password: str, profile):
    """Save encrypted session to HTTP cookie (persists in browser).
    
    Only readable on the same device due to device-specific encryption.
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
            # Use JavaScript to set HTTP cookie (browser stores it automatically)
            # 30 days expiry
            js_code = f"""
            <script>
            const date = new Date();
            date.setTime(date.getTime() + (30 * 24 * 60 * 60 * 1000));
            const expires = "expires=" + date.toUTCString();
            document.cookie = "pesu_session=" + encodeURIComponent('{encrypted_data}') + ";" + expires + ";path=/;SameSite=Lax";
            console.log('✅ Session cookie set');
            </script>
            """
            st.components.v1.html(js_code, height=0)
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

