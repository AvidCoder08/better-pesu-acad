#!/usr/bin/env python3
"""Test script to verify session persistence"""

import sys
import os
sys.path.insert(0, os.getcwd())

# Import the functions from login.py
import hashlib
import platform
import socket
import json
from datetime import datetime, timedelta

SESSION_DIR = ".sessions"
os.makedirs(SESSION_DIR, exist_ok=True)

def get_machine_id():
    """Generate a hardware-based machine ID that can't be spoofed"""
    try:
        machine_name = socket.gethostname()
        system = platform.system()
        processor = platform.processor()
        hw_string = f"{machine_name}:{system}:{processor}"
        machine_id = hashlib.sha256(hw_string.encode()).hexdigest()[:16]
        return machine_id
    except:
        return None

def get_device_key_file():
    """Get the path to the device key file stored locally"""
    return os.path.join(SESSION_DIR, ".device_key")

def get_or_create_device_key():
    """Get existing device key or create a new one"""
    import uuid
    key_file = get_device_key_file()
    machine_id = get_machine_id()
    
    if not machine_id:
        machine_id = str(uuid.uuid4())
    
    if os.path.exists(key_file):
        try:
            with open(key_file, 'r') as f:
                stored_id = f.read().strip()
            if stored_id == machine_id:
                return stored_id
        except:
            pass
    
    os.makedirs(SESSION_DIR, exist_ok=True)
    with open(key_file, 'w') as f:
        f.write(machine_id)
    
    try:
        os.chmod(key_file, 0o600)
    except:
        pass
    
    return machine_id

def get_session_id():
    """Get a truly device-specific session ID based on hardware"""
    device_key = get_or_create_device_key()
    return device_key

def get_session_file():
    """Get the session file path for this device"""
    session_id = get_session_id()
    return os.path.join(SESSION_DIR, f"session_{session_id}.json")

def load_session():
    """Load session data from the device-specific file"""
    session_file = get_session_file()
    
    if os.path.exists(session_file):
        try:
            with open(session_file, 'r') as f:
                data = json.load(f)
            
            # Verify this is the correct device
            if data.get('device_id') != get_session_id():
                print("ERROR: Device ID mismatch!")
                return None
            
            # Check if session has expired (24 hours)
            last_accessed = datetime.fromisoformat(data.get('last_accessed', datetime.now().isoformat()))
            if datetime.now() - last_accessed > timedelta(hours=24):
                print("ERROR: Session expired!")
                return None
            
            print("✓ Session loaded successfully")
            return data
        except Exception as e:
            print(f"ERROR loading session: {e}")
            import traceback
            traceback.print_exc()
            return None
    else:
        print(f"Session file not found: {session_file}")
    return None

# Test it
print("=== Testing Session Load ===")
print(f"Device ID: {get_session_id()}")
print(f"Session file: {get_session_file()}")
print()

data = load_session()
if data:
    print(f"Loaded username: {data.get('username')}")
    print(f"Device ID match: {data.get('device_id') == get_session_id()}")
else:
    print("Failed to load session")
