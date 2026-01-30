#!/usr/bin/env python3
"""Debug script to check device ID and session files"""

import hashlib
import platform
import socket
import os
import json
from datetime import datetime

SESSION_DIR = ".sessions"

def get_machine_id():
    """Generate a hardware-based machine ID that can't be spoofed"""
    try:
        # Combine multiple machine-specific identifiers
        machine_name = socket.gethostname()
        system = platform.system()
        processor = platform.processor()
        
        # Create a hash from hardware identifiers
        hw_string = f"{machine_name}:{system}:{processor}"
        machine_id = hashlib.sha256(hw_string.encode()).hexdigest()[:16]
        return machine_id
    except:
        return None

# Print machine details
print("=== Machine Information ===")
print(f"Hostname: {socket.gethostname()}")
print(f"System: {platform.system()}")
print(f"Processor: {platform.processor()}")
print(f"Computed Machine ID: {get_machine_id()}")
print()

# Check device key file
device_key_file = os.path.join(SESSION_DIR, ".device_key")
print("=== Device Key File ===")
print(f"Path: {device_key_file}")
if os.path.exists(device_key_file):
    with open(device_key_file, 'r') as f:
        stored_key = f.read().strip()
    print(f"Stored Key: {stored_key}")
    print(f"Match: {stored_key == get_machine_id()}")
else:
    print("File does not exist")
print()

# Check session files
print("=== Session Files ===")
if os.path.exists(SESSION_DIR):
    files = os.listdir(SESSION_DIR)
    if files:
        for f in files:
            if f.startswith("session_"):
                filepath = os.path.join(SESSION_DIR, f)
                print(f"\nFile: {f}")
                try:
                    with open(filepath, 'r') as fh:
                        data = json.load(fh)
                    print(f"  Device ID in file: {data.get('device_id', 'NOT FOUND')}")
                    print(f"  Username: {data.get('username', 'N/A')}")
                    print(f"  Created: {data.get('created_at', 'N/A')}")
                    print(f"  Last accessed: {data.get('last_accessed', 'N/A')}")
                except Exception as e:
                    print(f"  Error reading: {e}")
    else:
        print("No session files found")
else:
    print(f"Session directory '{SESSION_DIR}' does not exist")
