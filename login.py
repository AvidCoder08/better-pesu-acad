import streamlit as st
from firebase_utils import check_user_in_friends_list

st.set_page_config(page_title="Login - Better PESU", page_icon="🔐", layout="centered")

st.title("🔐 Better PESU Acad")
st.caption("Friends Only Access")

# Check if already logged in
if st.session_state.get('authenticated', False):
    st.success(f"✅ Logged in as {st.session_state.get('user_email')}")
    if st.button("Logout", type="secondary"):
        st.session_state.authenticated = False
        st.session_state.user_email = None
        st.rerun()
    st.stop()

st.divider()

with st.form("login_form"):
    email = st.text_input("Email", placeholder="friend@example.com")
    password = st.text_input("Password", type="password", placeholder="• • • • • • • •")
    
    submitted = st.form_submit_button("Login", type="primary", use_container_width=True)

if submitted:
    if not email or not password:
        st.error("Please enter both email and password")
    else:
        # Check if user is in friends list
        if check_user_in_friends_list(email):
            st.session_state.authenticated = True
            st.session_state.user_email = email
            st.success("✅ Welcome! You're now logged in.")
            st.balloons()
            st.rerun()
        else:
            st.error("❌ You're not authorized. Ask the owner to add your email!")

st.divider()
st.caption("This app is restricted to invited friends only. 🔒")
