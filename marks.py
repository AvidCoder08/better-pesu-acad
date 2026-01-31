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

st.title("📊 Grades & Results")

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
selected_sem = st.selectbox(
    "Choose a semester to view results:",
    options=list(range(1, current_sem + 1)),
    index=None,
    key="semester_selector",
)

async def fetch_results(semester):
    """Fetch results from PESU Academy API"""
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
            results = await pesu.get_results(semester)
        except AttributeError as ae:
            await pesu.close()
            return None, f"Results page structure not found. This might mean:\n- No results available for semester {semester} yet\n- Results are still being processed\n- Please try again later or contact support"
        except Exception as parse_error:
            await pesu.close()
            return None, f"Error parsing results: {str(parse_error)}"
        
        await pesu.close()
        
        if not results:
            return None, "No results found for this semester."
        
        return results, None
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback.print_exc()
        return None, f"Error fetching results: {error_msg}"

# Fetch button or auto-fetch
if st.button("Fetch Results", type="primary", use_container_width=True,icon=":material/azm:"):
    with st.spinner(f"Fetching semester {selected_sem} results..."):
        results, error = asyncio.run(fetch_results(selected_sem))
        
        if error:
            st.error(error)
            st.warning("Tips:\n- Make sure results are published as **Final** (not just provisional)\n- Try a different semester\n- Results might still be processing",icon=":material/lightbulb_2:")
        else:
            st.session_state.results = results
            st.success("Results fetched successfully!")
else:
    st.caption("Note: The library currently supports final published results. If you see provisional results on PESU Academy, they may not be available through this API yet.")

# Display results if available
if 'results' in st.session_state and st.session_state.results:
    results = st.session_state.results
    
    # Display SGPA
    st.markdown("---")
    sgpa_col1, sgpa_col2, sgpa_col3 = st.columns(3)
    with sgpa_col1:
        st.metric("📈 SGPA", f"{float(results.sgpa):.2f}")
    with sgpa_col2:
        st.metric("📚 Credits", int(results.credits) if isinstance(results.credits, (int, float, str)) else 0)
    with sgpa_col3:
        st.metric("📝 Courses", len(results.courses))
    
    # Display courses table
    st.markdown("---")
    st.subheader(f"Semester {selected_sem} Courses")
    
    courses_data = []
    for course in results.courses:
        # Calculate total marks and percentage
        total_marks = 0
        total_possible = 0
        
        for assessment in course.assessments:
            marks = int(assessment.marks) if isinstance(assessment.marks, (int, float, str)) else 0
            total = int(assessment.total) if isinstance(assessment.total, (int, float, str)) else 0
            total_marks += marks
            total_possible += total
        
        percentage = (total_marks / total_possible * 100) if total_possible > 0 else 0
        
        # Determine grade based on percentage (typical grading scale)
        if percentage >= 90:
            grade = "A+"
        elif percentage >= 80:
            grade = "A"
        elif percentage >= 70:
            grade = "B+"
        elif percentage >= 60:
            grade = "B"
        elif percentage >= 50:
            grade = "C"
        else:
            grade = "F"
        
        courses_data.append({
            "Course Code": course.code,
            "Course Title": course.title,
            "Credits": course.credits,
            "Total Marks": f"{total_marks}/{total_possible}",
            "Percentage": f"{percentage:.1f}%",
            "Grade": grade
        })
    
    # Display courses as dataframe
    courses_df = pd.DataFrame(courses_data)
    st.dataframe(
        courses_df,
        use_container_width=True,
        hide_index=True
    )
    
    # Display detailed assessments
    st.markdown("---")
    st.subheader("Assessment Details")
    
    # Create tabs for each course
    if courses_data:
        tabs = st.tabs([f"{course['Course Code']}" for course in courses_data])
        
        for idx, (tab, course) in enumerate(zip(tabs, results.courses)):
            with tab:
                st.markdown(f"**{course.title}**")
                
                assessment_data = []
                for assessment in course.assessments:
                    marks = int(assessment.marks) if isinstance(assessment.marks, (int, float, str)) else 0
                    total = int(assessment.total) if isinstance(assessment.total, (int, float, str)) else 0
                    percentage = f"{(marks/total*100):.1f}%" if total > 0 else "N/A"
                    assessment_data.append({
                        "Assessment": assessment.name,
                        "Marks Obtained": marks,
                        "Total Marks": total,
                        "Percentage": percentage
                    })
                
                assessment_df = pd.DataFrame(assessment_data)
                st.dataframe(
                    assessment_df,
                    use_container_width=True,
                    hide_index=True
                )
else:
    st.info(f"👆 Click the 'Fetch Results' button above to view semester {selected_sem} grades and marks.")
