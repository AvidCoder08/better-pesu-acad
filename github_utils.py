import os
import base64
from datetime import datetime
from dotenv import load_dotenv
import requests
import streamlit as st

load_dotenv()


def _get_github_config():
    """Get GitHub repository configuration from Streamlit secrets or environment variables."""
    # Try Streamlit secrets first
    try:
        token = st.secrets.get("github_token")
        repo = st.secrets.get("github_repo")
        branch = st.secrets.get("github_branch", "main")
    except (AttributeError, KeyError):
        token = None
        repo = None
        branch = "main"
    
    # Fallback to environment variables
    token = token or os.getenv("GITHUB_TOKEN")
    repo = repo or os.getenv("GITHUB_REPO")
    branch = branch or os.getenv("GITHUB_BRANCH", "main")
    
    if not token:
        raise RuntimeError("GITHUB_TOKEN not set. Add it to .streamlit/secrets.toml or set GITHUB_TOKEN env var.")
    if not repo:
        raise RuntimeError("GITHUB_REPO not set. Add it to .streamlit/secrets.toml or set GITHUB_REPO env var.")
    
    return {
        "token": token,
        "repo": repo,
        "branch": branch,
        "api_base": "https://api.github.com"
    }


def upload_to_github(file_bytes, file_path, commit_message=None):
    """
    Upload file bytes to GitHub repository and return the raw content URL.
    
    Args:
        file_bytes: The file content as bytes
        file_path: Path in the repo (e.g., "materials/CS101/file.pdf")
        commit_message: Optional commit message (defaults to auto-generated)
    
    Returns:
        str: Raw URL to access the file
    """
    config = _get_github_config()
    
    # Encode file content to base64
    content_base64 = base64.b64encode(file_bytes).decode('utf-8')
    
    # Default commit message
    if not commit_message:
        commit_message = f"Upload {file_path.split('/')[-1]}"
    
    # GitHub API endpoint
    url = f"{config['api_base']}/repos/{config['repo']}/contents/{file_path}"
    
    headers = {
        "Authorization": f"token {config['token']}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Check if file already exists (to get its SHA for updating)
    response = requests.get(url, headers=headers)
    sha = None
    if response.status_code == 200:
        sha = response.json().get("sha")
    
    # Prepare the payload
    payload = {
        "message": commit_message,
        "content": content_base64,
        "branch": config['branch']
    }
    
    # If file exists, include SHA to update it
    if sha:
        payload["sha"] = sha
    
    # Upload the file
    response = requests.put(url, headers=headers, json=payload)
    
    if response.status_code not in [200, 201]:
        raise RuntimeError(f"Failed to upload to GitHub: {response.status_code} - {response.text}")
    
    # Return the raw content URL using jsdelivr CDN for better browser compatibility
    # jsdelivr serves files with proper headers that allow viewing in browser without downloading
    jsdelivr_url = f"https://cdn.jsdelivr.net/gh/{config['repo']}@{config['branch']}/{file_path}"
    return jsdelivr_url


def delete_from_github(file_path):
    """
    Delete a file from GitHub repository.
    
    Args:
        file_path: Path in the repo (e.g., "materials/CS101/file.pdf")
    """
    config = _get_github_config()
    
    url = f"{config['api_base']}/repos/{config['repo']}/contents/{file_path}"
    
    headers = {
        "Authorization": f"token {config['token']}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Get the file's SHA (required for deletion)
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        # File doesn't exist or already deleted
        return
    
    sha = response.json().get("sha")
    
    # Delete the file
    payload = {
        "message": f"Delete {file_path.split('/')[-1]}",
        "sha": sha,
        "branch": config['branch']
    }
    
    response = requests.delete(url, headers=headers, json=payload)
    
    if response.status_code not in [200, 204]:
        raise RuntimeError(f"Failed to delete from GitHub: {response.status_code} - {response.text}")

def get_file_from_github(file_path):
    """
    Fetch file content from GitHub API (avoids CDN caching issues with raw URLs).
    
    Args:
        file_path: Path in the repo (e.g., "data/calendar_events.json")
    
    Returns:
        bytes: File content, or None if file doesn't exist
    """
    config = _get_github_config()
    
    url = f"{config['api_base']}/repos/{config['repo']}/contents/{file_path}"
    
    headers = {
        "Authorization": f"token {config['token']}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 404:
        return None
    
    response.raise_for_status()
    
    # Decode base64-encoded content from GitHub API
    file_data = response.json()
    content_base64 = file_data.get("content", "")
    
    if content_base64:
        return base64.b64decode(content_base64)
    
    return None

def get_github_file_url(file_path):
    """
    Get the raw URL for a file in the GitHub repository.
    
    Args:
        file_path: Path in the repo (e.g., "materials/CS101/file.pdf")
    
    Returns:
        str: Raw URL to access the file
    """
    config = _get_github_config()
    return f"https://raw.githubusercontent.com/{config['repo']}/{config['branch']}/{file_path}"


def save_user_profile(user_id, name, branch, email):
    """
    Save user profile to GitHub profiles.json file.
    
    Args:
        user_id: Firebase user ID
        name: User's full name
        branch: User's branch (CSE, AIML, etc.)
        email: User's email
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        import json
        config = _get_github_config()
        
        # Fetch existing profiles.json
        profiles_file = "profiles.json"
        url = f"{config['api_base']}/repos/{config['repo']}/contents/{profiles_file}"
        headers = {
            "Authorization": f"token {config['token']}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Try to get existing file
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            # File exists, decode and parse it
            file_data = response.json()
            content_base64 = file_data.get("content", "")
            sha = file_data.get("sha", "")
            profiles = json.loads(base64.b64decode(content_base64).decode('utf-8'))
        else:
            # File doesn't exist, create new dict
            profiles = {}
            sha = None
        
        # Update or add profile
        profiles[user_id] = {
            "name": name,
            "branch": branch,
            "email": email,
            "updated_at": datetime.now().isoformat()
        }
        
        # Encode to base64
        content_base64 = base64.b64encode(json.dumps(profiles, indent=2).encode('utf-8')).decode('utf-8')
        
        # Prepare payload
        payload = {
            "message": f"Update profile for {user_id}",
            "content": content_base64
        }
        
        if sha:
            payload["sha"] = sha
        
        # Upload to GitHub
        response = requests.put(url, json=payload, headers=headers)
        response.raise_for_status()
        
        return True
    except Exception as e:
        st.error(f"Error saving profile: {str(e)}")
        return False


def get_user_profile(user_id):
    """
    Get user profile from GitHub profiles.json file.
    
    Args:
        user_id: Firebase user ID
    
    Returns:
        dict: User profile data or None if not found
    """
    try:
        import json
        config = _get_github_config()
        
        # Fetch profiles.json
        profiles_file = "profiles.json"
        url = f"{config['api_base']}/repos/{config['repo']}/contents/{profiles_file}"
        headers = {
            "Authorization": f"token {config['token']}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            file_data = response.json()
            content_base64 = file_data.get("content", "")
            profiles = json.loads(base64.b64decode(content_base64).decode('utf-8'))
            
            return profiles.get(user_id)
        
        return None
    except Exception as e:
        st.error(f"Error getting profile: {str(e)}")
        return None


def save_user_profile(user_id, name, branch, email):
    """
    Save user profile to GitHub profiles.json file.
    
    Args:
        user_id: Firebase user ID
        name: User's full name
        branch: User's branch (CSE, AIML, etc.)
        email: User's email
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        import json
        config = _get_github_config()
        
        # Fetch existing profiles.json
        profiles_file = "profiles.json"
        url = f"{config['api_base']}/repos/{config['repo']}/contents/{profiles_file}"
        headers = {
            "Authorization": f"token {config['token']}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Try to get existing file
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            # File exists, decode and parse it
            file_data = response.json()
            content_base64 = file_data.get("content", "")
            sha = file_data.get("sha", "")
            profiles = json.loads(base64.b64decode(content_base64).decode('utf-8'))
        else:
            # File doesn't exist, create new dict
            profiles = {}
            sha = None
        
        # Update or add profile
        profiles[user_id] = {
            "name": name,
            "branch": branch,
            "email": email,
            "updated_at": datetime.now().isoformat()
        }
        
        # Encode to base64
        content_base64 = base64.b64encode(json.dumps(profiles, indent=2).encode('utf-8')).decode('utf-8')
        
        # Prepare payload
        payload = {
            "message": f"Update profile for {user_id}",
            "content": content_base64
        }
        
        if sha:
            payload["sha"] = sha
        
        # Upload to GitHub
        response = requests.put(url, json=payload, headers=headers)
        response.raise_for_status()
        
        return True
    except Exception as e:
        st.error(f"Error saving profile: {str(e)}")
        return False


def get_user_profile(user_id):
    """
    Get user profile from GitHub profiles.json file.
    
    Args:
        user_id: Firebase user ID
    
    Returns:
        dict: User profile data or None if not found
    """
    try:
        import json
        config = _get_github_config()
        
        # Fetch profiles.json
        profiles_file = "profiles.json"
        url = f"{config['api_base']}/repos/{config['repo']}/contents/{profiles_file}"
        headers = {
            "Authorization": f"token {config['token']}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            file_data = response.json()
            content_base64 = file_data.get("content", "")
            profiles = json.loads(base64.b64decode(content_base64).decode('utf-8'))
            
            return profiles.get(user_id)
        
        return None
    except Exception as e:
        st.error(f"Error getting profile: {str(e)}")
        return None
