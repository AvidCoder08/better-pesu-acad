import streamlit as st
import base64
from io import BytesIO

# Check if user is logged in
if not st.session_state.get('logged_in', False):
    st.warning("⚠️ Please login first")
    st.page_link("login.py", label="Go to Login", icon="🔐")
    st.stop()

st.header("Profile")

profile = st.session_state.profile

# Handle both dict and object profiles
if isinstance(profile, dict):
    personal = profile.get('personal', {})
else:
    personal = profile.personal

# Create layout with image on left and details on right
col_img, col_details = st.columns([1, 3])

with col_img:
    # Display profile image if available
    image_data = personal.get('image') if isinstance(personal, dict) else personal.image
    if image_data:
        try:
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            st.image(image_bytes, use_container_width=True)
        except:
            # If decoding fails, show placeholder
            st.markdown("""
            <div style="background-color: #f0f2f6; padding: 100px 20px; text-align: center; border-radius: 8px;">
                <p style="font-size: 48px; margin: 0;">👤</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        # Placeholder if no image
        st.markdown("""
        <div style="background-color: #f0f2f6; padding: 100px 20px; text-align: center; border-radius: 8px;">
            <p style="font-size: 48px; margin: 0;">👤</p>
        </div>
        """, unsafe_allow_html=True)

with col_details:
    # Create 3 columns for the details grid
    detail_col1, detail_col2, detail_col3 = st.columns(3)
    
    # Helper function to get value from dict or object
    def get_value(key):
        if isinstance(personal, dict):
            return personal.get(key, 'N/A')
        else:
            return getattr(personal, key, 'N/A')
    
    with detail_col1:
        st.markdown("**Name**")
        st.markdown(f"{get_value('name')}")
        st.markdown("")
        
        st.markdown("**PESU ID**")
        st.markdown(f"{get_value('pesu_id')}")
        st.markdown("")
        
        st.markdown("**SRN**")
        st.markdown(f"{get_value('srn')}")
        st.markdown("")
        
        st.markdown("**Program**")
        st.markdown(f"{get_value('program')}")
    
    with detail_col2:
        st.markdown("**Branch**")
        st.markdown(f"{get_value('branch')}")
        st.markdown("")

        st.markdown("**Semester**")
        st.markdown(f"{get_value('semester')}")
        st.markdown("")
        
        st.markdown("**Section**")
        st.markdown(f"{get_value('section')}")
    
    with detail_col3:
        st.markdown("**Email ID**")
        st.markdown(f"{get_value('email_id')}")
        st.markdown("")
        
        st.markdown("**Contact No**")
        st.markdown(f"{get_value('contact_no')}")
        st.markdown("")
        
        st.markdown("**Aadhar No**")
        aadhar = get_value('aadhar_no')
        st.markdown(f"{aadhar if aadhar != 'N/A' else 'N/A'}")
        st.markdown("")
        
        st.markdown("**Name as in aadhar**")
        name_aadhar = get_value('name_as_in_aadhar')
        st.markdown(f"{name_aadhar if name_aadhar != 'N/A' else 'N/A'}")
    
    # Edit button
    st.markdown("")
    if st.button("Edit", type="primary"):
        st.info("Edit functionality coming soon!")