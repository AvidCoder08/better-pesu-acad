import streamlit as st
import asyncio
import pandas as pd
from pesuacademy import PESUAcademy
from session_utils import restore_session_from_cookie

restore_session_from_cookie()

# Check if user is logged in
if not st.session_state.get('logged_in', False):
    st.warning("⚠️ Please login first")
    st.page_link("login.py", label="Go to Login", icon="🔐")
    st.stop()

st.title("📋 Attendance")

# Get profile to determine current semester
profile = st.session_state.profile
if isinstance(profile, dict):
    personal = profile.get('personal', {})
    sem_str = personal.get('semester', '1') if isinstance(personal, dict) else personal.get('semester', '1')
else:
    sem_str = profile.personal.semester

# Parse semester - handle both "Sem-2" and "2" formats
try:
    if isinstance(sem_str, str):
        current_sem = int(sem_str.split('-')[-1]) if '-' in sem_str else int(sem_str)
    else:
        current_sem = int(sem_str)
except:
    current_sem = 1

# Semester selector
st.subheader("Select Semester")
sem_options = list(range(1, current_sem + 1))
selected_sem = st.selectbox(
    "Choose a semester to view attendance:",
    options=sem_options,
    index=len(sem_options) - 1 if sem_options else 0,
    key="attendance_semester_selector",
)

async def fetch_attendance(semester):
    """Fetch attendance from PESU Academy API"""
    try:
        # Check if credentials are available
        if not st.session_state.get('pesu_username') or not st.session_state.get('pesu_password'):
            return None, "Credentials not found. Please login again."
        
        # Create a new authenticated session
        pesu = await PESUAcademy.login(
            st.session_state.pesu_username,
            st.session_state.pesu_password
        )
        
        if not pesu:
            return None, "Login failed. Please try again."
        
        try:
            attendance_data = await pesu.get_attendance(semester)
        except Exception as e:
            await pesu.close()
            return None, f"Error fetching attendance: {str(e)}"
        
        await pesu.close()
        
        if not attendance_data or semester not in attendance_data:
            return None, f"No attendance data found for semester {semester}."
        
        return attendance_data[semester], None
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback.print_exc()
        return None, f"Error fetching attendance: {error_msg}"

# Fetch button
if st.button("📥 Fetch Attendance", type="primary", use_container_width=True):
    with st.spinner(f"Fetching semester {selected_sem} attendance..."):
        courses, error = asyncio.run(fetch_attendance(selected_sem))
        
        if error:
            st.error(error)
        else:
            st.session_state.attendance_data = courses
            st.success("Attendance fetched successfully!")
else:
    st.caption("Click 'Fetch Attendance' to load your attendance data")

# Display attendance if available
if 'attendance_data' in st.session_state and st.session_state.attendance_data:
    courses = st.session_state.attendance_data
    
    # Create attendance data
    attendance_list = []
    total_classes_attended = 0
    total_classes = 0
    
    for course in courses:
        if course.attendance:
            attended = course.attendance.attended if course.attendance.attended is not None else 0
            total = course.attendance.total if course.attendance.total is not None else 0
            percentage = course.attendance.percentage if course.attendance.percentage is not None else 0
            
            total_classes_attended += attended
            total_classes += total
            
            # Color code the attendance percentage (75% is the cutoff)
            if percentage >= 75:
                status = "✅ Good"
            elif percentage >= 70:
                status = "⚠️ Danger"
            else:
                status = "🚨 Critical"
            
            attendance_list.append({
                "Course Code": course.code,
                "Course Title": course.title,
                "Attended": attended,
                "Total Classes": total,
                "Attendance %": f"{percentage:.1f}%",
                "Status": status
            })
        else:
            # No attendance data for this course
            attendance_list.append({
                "Course Code": course.code,
                "Course Title": course.title,
                "Attended": "N/A",
                "Total Classes": "N/A",
                "Attendance %": "N/A",
                "Status": "No data"
            })
    
    # Display overall summary
    st.markdown("---")
    st.subheader("📊 Overall Summary")
    
    if total_classes > 0:
        overall_percentage = (total_classes_attended / total_classes) * 100
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Classes Attended", total_classes_attended)
        with col2:
            st.metric("Total Classes", total_classes)
        with col3:
            st.metric("Overall Attendance %", f"{overall_percentage:.1f}%")
        with col4:
            if overall_percentage >= 85:
                st.metric("Status", "✅ Good")
            elif overall_percentage >= 75:
                st.metric("Status", "✅ Safe")
            elif overall_percentage >= 70:
                st.error("⚠️ Danger")
            else:
                st.error("🚨 Critical")
    else:
        st.info("No attendance data available for this semester.")
    
    # Display detailed attendance table
    st.markdown("---")
    st.subheader("📑 Course-wise Attendance")
    
    attendance_df = pd.DataFrame(attendance_list)
    st.dataframe(
        attendance_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Attendance %": st.column_config.TextColumn(
                "Attendance %",
                width="medium"
            ),
            "Status": st.column_config.TextColumn(
                "Status",
                width="medium"
            )
        }
    )
    
    # Display course cards with attendance bars
    st.markdown("---")
    st.subheader("📈 Attendance Details")
    
    for course in courses:
        if course.attendance and course.attendance.total and course.attendance.total > 0:
            attended = course.attendance.attended if course.attendance.attended is not None else 0
            total = course.attendance.total if course.attendance.total is not None else 0
            percentage = course.attendance.percentage if course.attendance.percentage is not None else 0
            
            with st.expander(f"**{course.code}** - {course.title}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.progress(
                        min(percentage / 100, 1.0),
                        text=f"{percentage:.1f}% ({attended}/{total} classes)"
                    )
                
                with col2:
                    if percentage >= 85:
                        st.success("✅")
                    elif percentage >= 75:
                        st.info("✅")
                    elif percentage >= 70:
                        st.error("⚠️")
                    else:
                        st.error("🚨")
                
                # Additional details
                st.metric(f"Classes Attended", f"{attended} out of {total}")
                
                # Calculate classes needed to reach 75%
                classes_needed_for_cutoff = int((total * 0.75) - attended)
                if percentage < 75:
                    if classes_needed_for_cutoff > 0:
                        if percentage >= 70:
                            st.error(f"🚨 **DANGER:** You need to attend at least **{classes_needed_for_cutoff}** more classes to reach 75% attendance!")
                        else:
                            st.error(f"🚨 **CRITICAL:** You need to attend at least **{classes_needed_for_cutoff}** more classes to reach 75% attendance!")
                    else:
                        st.error("🚨 **CRITICAL:** You are below 75% attendance cutoff!")
        else:
            with st.expander(f"**{course.code}** - {course.title}"):
                st.info("No attendance data available for this course yet.")

else:
    st.info(f"👆 Click 'Fetch Attendance' above to view semester {selected_sem} attendance data.")
