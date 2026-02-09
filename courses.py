import streamlit as st
from datetime import datetime
from urllib.parse import quote
from session_utils import restore_session_from_cookie
from github_utils import upload_to_github, delete_from_github
from materials_utils import add_material, get_materials_by_section, delete_material

restore_session_from_cookie()

st.title("📚 Course Materials")
st.caption("Share & manage course materials organized by subject")

# Get profile info
profile = st.session_state.profile

if profile is None:
    user_ids = []
elif isinstance(profile, dict):
    personal = profile.get('personal', {})
    user_ids = personal.get('puid', []) if isinstance(personal, dict) else personal.get('puid', [])
else:
    personal = profile.personal if hasattr(profile, 'personal') else None
    user_ids = personal.puid if personal and hasattr(personal, 'puid') else []

st.markdown("---")
st.subheader("📤 Upload Materials")
st.caption("Upload course materials to share with others")

with st.form("upload_materials", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        course_code = st.text_input("Course Code", placeholder="UE22CS202", help="e.g., UE22CS202")
    
    with col2:
        course_title = st.text_input("Course Title", placeholder="Data Structures", help="e.g., Data Structures")
    
    files = st.file_uploader("Upload files", accept_multiple_files=True, help="Select one or more files to upload")
    
    submit = st.form_submit_button("Upload", type="primary", use_container_width=True)

    if submit:
        if not course_code.strip():
            st.error("Course code is required! 📝")
        elif not course_title.strip():
            st.error("Course title is required! 📝")
        elif not files:
            st.error("Please select at least one file to upload! 📁")
        else:
            try:
                with st.spinner(f"Uploading {len(files)} file(s)..."):
                    for uploaded_file in files:
                        # Create storage path - organized by subject/course code
                        storage_path = f"course_materials/{course_code.strip()}/{uploaded_file.name}"
                        
                        # Upload to GitHub
                        public_url = upload_to_github(
                            uploaded_file.getvalue(), 
                            storage_path, 
                            commit_message=f"Upload {course_code.strip()}: {uploaded_file.name}"
                        )
                        
                        # Add to materials database
                        add_material(
                            course_code=course_code.strip(),
                            course_title=course_title.strip(),
                            filename=uploaded_file.name,
                            file_url=public_url,
                            section=None,  # No section classification
                            uploaded_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            uploaded_by=user_ids[0] if user_ids else "Unknown"
                        )
                
                st.success(f"✅ Successfully uploaded {len(files)} file(s)!")
                
            except Exception as e:
                st.error(f"Upload failed: {str(e)}")

st.markdown("---")
st.subheader("📚 Available Materials")

try:
    # Get all materials (not filtered by section anymore)
    materials = get_materials_by_section(None, None)
    
    if not materials:
        st.info("No materials uploaded yet. Be the first to share! 🚀")
    else:
        # Group materials by course code
        materials_by_course = {}
        for material in materials:
            course_code = material.get("course_code", "Unknown")
            if course_code not in materials_by_course:
                materials_by_course[course_code] = []
            materials_by_course[course_code].append(material)
        
        # Display materials organized by course
        for course_code in sorted(materials_by_course.keys()):
            course_materials = materials_by_course[course_code]
            
            # Get course title from first material entry
            course_title = course_materials[0].get("course_title", course_code)
            
            with st.expander(f"📘 {course_code} - {course_title}", expanded=False):
                # Sort by upload date
                course_materials = sorted(course_materials, key=lambda x: x.get("uploaded_at", ""), reverse=True)
                
                for i, material in enumerate(course_materials):
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        filename = material.get("filename", "file")
                        uploaded_at = material.get("uploaded_at", "Unknown date")
                        uploaded_by = material.get("uploaded_by", "Unknown user")
                        file_url = material.get("file_url")
                        
                        st.markdown(f"**📄 {filename}**")
                        st.caption(f"Uploaded: {uploaded_at}")
                        
                        if file_url:
                            # Use Mozilla PDF.js viewer to open PDF inline in browser
                            viewer_url = f"https://mozilla.github.io/pdf.js/web/viewer.html?file={quote(file_url)}"
                            st.link_button("View File", viewer_url, type="primary", use_container_width=True)
                    
                    with col2:
                        # Show delete button (only for uploader)
                        if st.button("🗑️", key=f"del_{course_code}_{i}", help="Delete this material"):
                            try:
                                storage_path = f"course_materials/{course_code}/{filename}"
                                delete_from_github(storage_path)
                                delete_material(course_code, filename)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to delete: {str(e)}")
                    
                    st.divider()

except Exception as e:
    st.error(f"Error loading materials: {str(e)}")

