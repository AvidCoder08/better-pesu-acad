import requests
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

# Firebase Web API Key (get from Firebase Console → Project Settings)
FIREBASE_WEB_API_KEY = os.getenv("FIREBASE_WEB_API_KEY")

if not FIREBASE_WEB_API_KEY:
    raise RuntimeError(
        "FIREBASE_WEB_API_KEY not found. Get it from Firebase Console → Project Settings → General tab"
    )

FIREBASE_AUTH_URL = "https://identitytoolkit.googleapis.com/v1/accounts"


def sign_up(email: str, password: str) -> dict:
    """
    Create a new user account with Firebase Authentication.
    
    Args:
        email: User's email
        password: User's password (min 6 characters)
    
    Returns:
        dict with user info or error
    """
    try:
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        response = requests.post(
            f"{FIREBASE_AUTH_URL}:signUp?key={FIREBASE_WEB_API_KEY}",
            json=payload,
            timeout=10
        )
        
        data = response.json()
        
        if response.status_code == 200:
            return {
                "success": True,
                "user_id": data.get("localId"),
                "email": data.get("email"),
                "id_token": data.get("idToken"),
                "refresh_token": data.get("refreshToken")
            }
        else:
            error_msg = data.get("error", {}).get("message", "Unknown error")
            return {
                "success": False,
                "error": _parse_firebase_error(error_msg)
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Connection error: {str(e)}"
        }


def sign_in(email: str, password: str) -> dict:
    """
    Authenticate user with Firebase Authentication.
    
    Args:
        email: User's email
        password: User's password
    
    Returns:
        dict with user info or error
    """
    try:
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        response = requests.post(
            f"{FIREBASE_AUTH_URL}:signInWithPassword?key={FIREBASE_WEB_API_KEY}",
            json=payload,
            timeout=10
        )
        
        data = response.json()
        
        if response.status_code == 200:
            return {
                "success": True,
                "user_id": data.get("localId"),
                "email": data.get("email"),
                "id_token": data.get("idToken"),
                "refresh_token": data.get("refreshToken")
            }
        else:
            error_msg = data.get("error", {}).get("message", "Unknown error")
            return {
                "success": False,
                "error": _parse_firebase_error(error_msg)
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Connection error: {str(e)}"
        }


def verify_id_token(id_token: str) -> dict:
    """
    Verify and get user info from ID token.
    
    Args:
        id_token: Firebase ID token
    
    Returns:
        dict with user info or error
    """
    try:
        payload = {
            "idToken": id_token
        }
        
        response = requests.post(
            f"{FIREBASE_AUTH_URL}:lookup?key={FIREBASE_WEB_API_KEY}",
            json=payload,
            timeout=10
        )
        
        data = response.json()
        
        if response.status_code == 200 and data.get("users"):
            user = data["users"][0]
            return {
                "success": True,
                "user_id": user.get("localId"),
                "email": user.get("email"),
                "email_verified": user.get("emailVerified", False)
            }
        else:
            return {
                "success": False,
                "error": "Invalid token"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Verification error: {str(e)}"
        }


def send_password_reset(email: str) -> dict:
    """
    Send a password reset email to the user.
    
    Args:
        email: User's email address
    
    Returns:
        dict with success status or error
    """
    try:
        payload = {
            "email": email,
            "requestType": "PASSWORD_RESET"
        }
        
        response = requests.post(
            f"{FIREBASE_AUTH_URL}:sendOobCode?key={FIREBASE_WEB_API_KEY}",
            json=payload,
            timeout=10
        )
        
        data = response.json()
        
        if response.status_code == 200:
            return {
                "success": True,
                "message": f"Password reset email sent to {email}"
            }
        else:
            error_msg = data.get("error", {}).get("message", "Unknown error")
            return {
                "success": False,
                "error": _parse_firebase_error(error_msg)
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Connection error: {str(e)}"
        }


def confirm_password_reset(reset_code: str, new_password: str) -> dict:
    """
    Confirm password reset with the reset code.
    
    Args:
        reset_code: The password reset code from email
        new_password: The new password (min 6 characters)
    
    Returns:
        dict with success status or error
    """
    try:
        payload = {
            "oobCode": reset_code,
            "newPassword": new_password
        }
        
        response = requests.post(
            f"{FIREBASE_AUTH_URL}:resetPassword?key={FIREBASE_WEB_API_KEY}",
            json=payload,
            timeout=10
        )
        
        data = response.json()
        
        if response.status_code == 200:
            return {
                "success": True,
                "email": data.get("email"),
                "message": "Password reset successfully!"
            }
        else:
            error_msg = data.get("error", {}).get("message", "Unknown error")
            return {
                "success": False,
                "error": _parse_firebase_error(error_msg)
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Connection error: {str(e)}"
        }


def send_email_verification(email: str) -> dict:
    """
    Send an email verification link to the user.
    
    Args:
        email: User's email address
    
    Returns:
        dict with success status or error
    """
    try:
        payload = {
            "email": email,
            "requestType": "VERIFY_EMAIL"
        }
        
        response = requests.post(
            f"{FIREBASE_AUTH_URL}:sendOobCode?key={FIREBASE_WEB_API_KEY}",
            json=payload,
            timeout=10
        )
        
        data = response.json()
        
        if response.status_code == 200:
            return {
                "success": True,
                "message": f"Verification email sent to {email}"
            }
        else:
            error_msg = data.get("error", {}).get("message", "Unknown error")
            return {
                "success": False,
                "error": _parse_firebase_error(error_msg)
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Connection error: {str(e)}"
        }


def _parse_firebase_error(error_msg: str) -> str:
    """Parse Firebase error messages to user-friendly text."""
    errors = {
        "EMAIL_EXISTS": "This email is already registered",
        "OPERATION_NOT_ALLOWED": "Email/password accounts are not enabled",
        "TOO_MANY_ATTEMPTS_LOGIN_RETRY_ACCOUNT": "Too many failed login attempts. Try again later",
        "USER_DISABLED": "This account has been disabled",
        "INVALID_EMAIL": "Invalid email address",
        "WEAK_PASSWORD": "Password is too weak (min 6 characters)",
        "INVALID_LOGIN_CREDENTIALS": "Email or password is incorrect",
        "USER_NOT_FOUND": "No account found with this email"
    }
    
    for key, message in errors.items():
        if key in error_msg:
            return message
    
    return error_msg
