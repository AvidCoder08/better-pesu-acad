import streamlit as st
import asyncio
from pesuacademy import PESUAcademy
import json
import os
from session_utils import restore_session_from_cookie
from role_utils import get_class_id, is_cr
from firebase_utils import get_firestore_client

restore_session_from_cookie()

# Check if user is logged in
if not st.session_state.get('logged_in', False):
    st.warning("⚠️ Please login first")
    st.page_link("login.py", label="Go to Login", icon="🔐")
    st.stop()

st.title("📚 Courses & Materials")

# Get profile early for role checks
profile = st.session_state.profile

material_source = st.radio(
    "Choose material source:",
    options=["PESU Academy", "Teacher Files"],
    horizontal=True,
)

if material_source == "Teacher Files":
    try:
        db = get_firestore_client()
    except Exception as exc:
        st.error(f"Teacher files are unavailable: {exc}")
        st.stop()

    class_id = get_class_id(profile)
    st.subheader("Teacher Files")
    st.caption(f"Class: {class_id}")

    if is_cr(profile):
        st.page_link("admin.py", label="Go to Class Admin", icon="🛡️")

    course_filter = st.text_input("Filter by course code (optional)", placeholder="UE22CS202")
    materials = []
    query = db.collection("teacher_materials").where("class_id", "==", class_id)
    if course_filter.strip():
        query = query.where("course_code", "==", course_filter.strip())

    for doc in query.stream():
        data = doc.to_dict() or {}
        data["id"] = doc.id
        materials.append(data)

    if not materials:
        st.info("No teacher materials found for your class.")
    else:
        materials = sorted(materials, key=lambda x: x.get("uploaded_at", ""), reverse=True)
        for item in materials:
            title = item.get("course_title") or item.get("course_code") or "Course"
            filename = item.get("filename", "file")
            with st.expander(f"{title} • {filename}"):
                st.write(f"Course: {item.get('course_code', '')}")
                st.write(f"Uploaded at: {item.get('uploaded_at', '')}")
                drive_link = item.get("drive_link")
                if drive_link:
                    st.link_button("Open in Google Drive", drive_link, type="primary")
                else:
                    st.error("Drive link unavailable")

    st.stop()

# Get profile to determine current semester
if isinstance(profile, dict):
    personal = profile.get('personal', {})
    sem_str = personal.get('semester', '1') if isinstance(personal, dict) else personal.get('semester', '1')
else:
    sem_str = profile.personal.semester

# Parse semester
try:
    if isinstance(sem_str, str):
        current_sem = int(sem_str.split('-')[-1]) if '-' in sem_str else int(sem_str)
    else:
        current_sem = int(sem_str)
except:
    current_sem = 1

async def fetch_courses(semester):
    """Fetch courses from PESU Academy API"""
    try:
        pesu = await PESUAcademy.login(
            st.session_state.pesu_username,
            st.session_state.pesu_password
        )
        courses = await pesu.get_courses(semester)
        await pesu.close()
        return courses, None
    except Exception as e:
        return None, str(e)

async def fetch_units(course_id):
    """Fetch units for a course"""
    try:
        pesu = await PESUAcademy.login(
            st.session_state.pesu_username,
            st.session_state.pesu_password
        )
        units = await pesu.get_units_for_course(course_id)
        await pesu.close()
        return units, None
    except Exception as e:
        return None, str(e)

async def fetch_topics(unit_id):
    """Fetch topics for a unit"""
    try:
        pesu = await PESUAcademy.login(
            st.session_state.pesu_username,
            st.session_state.pesu_password
        )
        topics = await pesu.get_topics_for_unit(unit_id)
        await pesu.close()
        return topics, None
    except Exception as e:
        return None, str(e)

async def fetch_materials(topic, material_type_id):
    """Fetch material links for a topic"""
    try:
        pesu = await PESUAcademy.login(
            st.session_state.pesu_username,
            st.session_state.pesu_password
        )
        materials = await pesu.get_material_links(topic, material_type_id)
        await pesu.close()
        return materials, None
    except Exception as e:
        return None, str(e)

# Semester selector
selected_sem = st.selectbox(
    "Select Semester:",
    options=list(range(1, current_sem + 1)),
    index=current_sem - 1,
    key="course_semester_selector"
)

# Fetch courses button
if st.button("📥 Fetch Courses", type="primary", use_container_width=True):
    with st.spinner(f"Fetching semester {selected_sem} courses..."):
        courses_dict, error = asyncio.run(fetch_courses(selected_sem))
        
        if error:
            st.error(f"Failed to fetch courses: {error}")
        elif courses_dict:
            # Store courses in session state
            st.session_state.courses = courses_dict.get(selected_sem, [])
            st.success(f"Fetched {len(st.session_state.courses)} courses!",icon=":material/check:")
        else:
            st.error("No courses data returned")

# Display courses if available
if 'courses' in st.session_state and st.session_state.courses:
    st.markdown("---")
    st.subheader(f"Semester {selected_sem} Courses")
    
    # Create course selection
    course_options = {f"{course.code} - {course.title}": course for course in st.session_state.courses}
    
    selected_course_name = st.selectbox(
        "Select Course:",
        options=list(course_options.keys()),
        key="selected_course"
    )
    
    if selected_course_name:
        selected_course = course_options[selected_course_name]
        
        # Display course info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Course Code", selected_course.code)
        with col2:
            st.metric("Type", selected_course.type)
        with col3:
            st.metric("Status", selected_course.status)
        
        # Fetch units for selected course
        if st.button("📖 Load Units & Materials", type="secondary"):
            with st.spinner("Loading units..."):
                units, error = asyncio.run(fetch_units(selected_course.id))
                
                if error:
                    st.error(f"Failed to fetch units: {error}")
                elif units:
                    st.session_state.current_units = units
                    st.session_state.current_course_id = selected_course.id
                    st.success(f"Loaded {len(units)} units!",icon=":material/check:")
                else:
                    st.info("No units found for this course")
        
        # Display units and materials
        if 'current_units' in st.session_state and st.session_state.current_units and st.session_state.get('current_course_id') == selected_course.id:
            st.markdown("---")
            st.subheader("📑 Course Materials")
            
            for unit in st.session_state.current_units:
                with st.expander(f"📘 {unit.title}"):
                    if st.button(f"Load Topics for {unit.title}", key=f"load_topics_{unit.id}"):
                        with st.spinner(f"Loading topics for {unit.title}..."):
                            topics, error = asyncio.run(fetch_topics(unit.id))
                            
                            if error:
                                st.error(f"Failed to fetch topics: {error}")
                            else:
                                st.session_state[f"topics_{unit.id}"] = topics
                                st.rerun()
                    
                    # Display topics if loaded
                    if f"topics_{unit.id}" in st.session_state:
                        topics = st.session_state[f"topics_{unit.id}"]
                        
                        for topic in topics:
                            st.markdown(f"**📝 {topic.title}**")
                            
                            # Material type selector
                            material_types = {
                                "Lecture Notes": "1",
                                "Assignments": "2",
                                "Question Papers": "3",
                                "Lab Materials": "4",
                                "Additional Resources": "5"
                            }
                            
                            cols = st.columns(len(material_types))
                            for idx, (mat_name, mat_id) in enumerate(material_types.items()):
                                with cols[idx]:
                                    if st.button(mat_name, key=f"mat_{topic.id}_{mat_id}", use_container_width=True):
                                        with st.spinner(f"Fetching {mat_name}..."):
                                            materials, error = asyncio.run(fetch_materials(topic, mat_id))
                                            
                                            if error:
                                                st.error(f"Error: {error}")
                                            elif not materials:
                                                st.info(f"No {mat_name} available")
                                            else:
                                                st.session_state[f"materials_{topic.id}_{mat_id}"] = materials
                                                st.rerun()
                            
                            # Display materials if loaded
                            for mat_name, mat_id in material_types.items():
                                mat_key = f"materials_{topic.id}_{mat_id}"
                                if mat_key in st.session_state:
                                    materials = st.session_state[mat_key]
                                    if materials:
                                        st.markdown(f"**{mat_name}:**")
                                        for material in materials:
                                            if material.is_pdf:
                                                st.markdown(f"📄 [{material.title}]({material.url})")
                                            else:
                                                st.markdown(f"🔗 [{material.title}]({material.url})")
                            
                            st.markdown("---")

else:
    st.info("👆 Click 'Fetch Courses' to load your semester courses")
