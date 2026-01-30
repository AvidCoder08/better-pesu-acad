import streamlit as st
import json
import os

st.title("Session Debug Info")

SESSION_DIR = ".sessions"

# Show machine ID
import hashlib
import platform
import socket

def get_machine_id():
    try:
        machine_name = socket.gethostname()
        system = platform.system()
        processor = platform.processor()
        hw_string = f"{machine_name}:{system}:{processor}"
        machine_id = hashlib.sha256(hw_string.encode()).hexdigest()[:16]
        return machine_id
    except:
        return None

machine_id = get_machine_id()
st.write(f"**Machine ID:** `{machine_id}`")

# Show device key file
device_key_file = os.path.join(SESSION_DIR, ".device_key")
st.write(f"**Device Key File:** `{device_key_file}`")
st.write(f"**Exists:** {os.path.exists(device_key_file)}")

# Show session files
st.write("**Session Files:**")
if os.path.exists(SESSION_DIR):
    files = os.listdir(SESSION_DIR)
    for f in files:
        if f.startswith("session_"):
            filepath = os.path.join(SESSION_DIR, f)
            st.write(f"- `{f}`")
            try:
                with open(filepath, 'r') as fh:
                    data = json.load(fh)
                st.write(f"  - Username: `{data.get('username')}`")
                st.write(f"  - Device ID: `{data.get('device_id')}`")
            except Exception as e:
                st.write(f"  - Error: {e}")
else:
    st.write("No session directory")

# Show current session state
st.write("**Current Session State:**")
st.write(f"- logged_in: {st.session_state.get('logged_in', False)}")
st.write(f"- profile: {bool(st.session_state.get('profile'))}")
st.write(f"- pesu_username: {st.session_state.get('pesu_username', 'None')}")

if st.button("Clear All Sessions"):
    import shutil
    if os.path.exists(SESSION_DIR):
        shutil.rmtree(SESSION_DIR)
        os.makedirs(SESSION_DIR)
        st.success("Sessions cleared!")
        st.rerun()
