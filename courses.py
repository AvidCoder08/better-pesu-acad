import streamlit as st
from datetime import datetime
from session_utils import restore_session_from_cookie
from github_utils import upload_to_github, delete_from_github, MAX_FILE_SIZE
from materials_utils import add_material, get_materials_by_section, delete_material, update_material_type

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

# Create tabs
tab1, tab2 = st.tabs(["Browse Materials", "Upload Materials"])

with tab2:
    st.subheader("📤 Upload Materials")
    st.caption("Upload course materials to share with others")

    with st.form("upload_materials", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            course_code = st.text_input("Course Code", placeholder="UE22CS202", help="e.g., UE22CS202")
        
        with col2:
            course_title = st.text_input("Course Title", placeholder="Data Structures", help="e.g., Data Structures")
        
        material_type = st.selectbox(
            "Material Type",
            options=["Slides", "Notes", "Assignments", "Question Papers", "Solutions", "Lab Materials", "Other"],
            index=None,
            placeholder="Select type"
        )
        
        files = st.file_uploader("Upload files", accept_multiple_files=True, help="Select one or more files to upload")
        
        submit = st.form_submit_button("Upload", type="primary", use_container_width=True)

        if submit:
            if not course_code.strip():
                st.error("Course code is required! 📝")
            elif not course_title.strip():
                st.error("Course title is required! 📝")
            elif not material_type:
                st.error("Please select a material type! 🏷️")
            elif not files:
                st.error("Please select at least one file to upload! 📁")
            else:
                # Check file sizes
                max_size_mb = MAX_FILE_SIZE / (1024 * 1024)
                oversized_files = []
                for uploaded_file in files:
                    file_size = len(uploaded_file.getvalue())
                    if file_size > MAX_FILE_SIZE:
                        file_size_mb = file_size / (1024 * 1024)
                        oversized_files.append(f"{uploaded_file.name} ({file_size_mb:.2f}MB)")
                
                if oversized_files:
                    st.error(f"⚠️ The following files exceed the {max_size_mb:.0f}MB limit:\n" + "\n".join(oversized_files))
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
                                    uploaded_by=user_ids[0] if user_ids else "Unknown",
                                    material_type=material_type
                                )
                        
                        st.success(f"✅ Successfully uploaded {len(files)} file(s)!")
                        
                    except Exception as e:
                        st.error(f"Upload failed: {str(e)}")

with tab1:
    st.subheader("📚 Available Materials")

    try:
        # Get all materials (not filtered by section anymore)
        materials = get_materials_by_section(None, None)
        
        if not materials:
            st.info("No materials uploaded yet. Be the first to share! 🚀")
        else:
            # Extract unique courses and material types
            all_courses = {}
            material_types = set()
            for material in materials:
                course_code = material.get("course_code", "Unknown")
                course_title = material.get("course_title", course_code)
                all_courses[course_code] = course_title
                
                mat_type = material.get("material_type", "Other")
                material_types.add(mat_type)
            
            # Filter dropdowns
            col1, col2 = st.columns(2)
            with col1:
                selected_course = st.selectbox(
                    "Select Subject",
                    options=[f"{code} - {title}" for code, title in sorted(all_courses.items())],
                    index=None,
                    placeholder="Choose a subject..."
                )
            with col2:
                selected_type = st.selectbox(
                    "Select Material Type",
                    options=sorted(material_types),
                    index=None,
                    placeholder="Choose material type..."
                )
            
            # Only show materials if BOTH filters are selected
            if selected_course and selected_type:
                # Apply filters
                course_code_filter = selected_course.split(" - ")[0]
                filtered_materials = [m for m in materials 
                                    if m.get("course_code") == course_code_filter 
                                    and m.get("material_type") == selected_type]
                
                if not filtered_materials:
                    st.info("No materials found for this selection. 🔍")
                else:
                    # Display materials (no grouping needed since we filtered to one course)
                    course_materials = sorted(filtered_materials, key=lambda x: x.get("uploaded_at", ""), reverse=True)
                    
                    st.markdown(f"### 📘 {selected_course}")
                    st.caption(f"Showing {len(course_materials)} {selected_type.lower()} file(s)")
                    st.markdown("---")
                    
                    for i, material in enumerate(course_materials):
                        filename = material.get("filename", "file")
                        uploaded_at = material.get("uploaded_at", "Unknown date")
                        uploaded_by = material.get("uploaded_by", "Unknown user")
                        material_type = material.get("material_type", "Other")
                        file_url = material.get("file_url")
                        course_code = material.get("course_code", "Unknown")
                        
                        col1, col2, col3 = st.columns([3, 1, 0.3])
                        
                        with col1:
                            st.markdown(f"**📄 {filename}**")
                            st.caption(f"Uploaded: {uploaded_at}")
                            
                            if file_url:
                                st.link_button("View File", file_url, type="primary", use_container_width=True)
                        
                        with col2:
                            # Edit material type
                            edit_key = f"edit_{course_code}_{i}"
                            if st.button("✏️ Edit Type", key=edit_key, use_container_width=True):
                                st.session_state[f"editing_{course_code}_{i}"] = True
                        
                        with col3:
                            # Show delete button
                            if st.button("🗑️", key=f"del_{course_code}_{i}", help="Delete this material"):
                                try:
                                    storage_path = f"course_materials/{course_code}/{filename}"
                                    delete_from_github(storage_path)
                                    delete_material(course_code, filename)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Failed to delete: {str(e)}")
                        
                        # Show edit dialog if editing this material
                        if st.session_state.get(f"editing_{course_code}_{i}", False):
                            with st.container():
                                st.markdown("**Edit Material Type:**")
                                new_type = st.selectbox(
                                    "Select new type",
                                    options=["Slides", "Notes", "Assignments", "Question Papers", "Solutions", "Lab Materials", "Other"],
                                    index=["Slides", "Notes", "Assignments", "Question Papers", "Solutions", "Lab Materials", "Other"].index(material_type) if material_type in ["Slides", "Notes", "Assignments", "Question Papers", "Solutions", "Lab Materials", "Other"] else 6,
                                    key=f"type_select_{course_code}_{i}"
                                )
                                col_save, col_cancel = st.columns(2)
                                with col_save:
                                    if st.button("💾 Save", key=f"save_{course_code}_{i}", use_container_width=True):
                                        update_material_type(course_code, filename, new_type)
                                        st.session_state[f"editing_{course_code}_{i}"] = False
                                        st.rerun()
                                with col_cancel:
                                    if st.button("❌ Cancel", key=f"cancel_{course_code}_{i}", use_container_width=True):
                                        st.session_state[f"editing_{course_code}_{i}"] = False
                                        st.rerun()
                        
                        st.divider()
            else:
                st.info("👆 Select both a subject and material type to view files")

    except Exception as e:
        st.error(f"Error loading materials: {str(e)}")

