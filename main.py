import streamlit as st
from dotenv import load_dotenv
from datetime import datetime
import time
from firebase_auth import sign_up, sign_in, send_password_reset, confirm_password_reset
from github_utils import upload_to_github, delete_from_github
from materials_utils import add_material, get_materials_by_section, delete_material

load_dotenv()

st.set_page_config(page_title="Better PESU", page_icon=":school:", layout="wide")

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None
if 'user_branch' not in st.session_state:
    st.session_state.user_branch = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'id_token' not in st.session_state:
    st.session_state.id_token = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'login'
if 'tasks' not in st.session_state:
    st.session_state.tasks = []

logo_svg = """
<svg width="450" height="50">
  <text x="0" y="40" font-family="Roboto" font-size="40" fill='#fafafa'>Better PESU Acad (Beta)</text>
</svg>
"""
st.logo(logo_svg)
st.markdown("""
<style>
html, body, [class*="css"]  {
  font-family: system-ui, -apple-system, BlinkMacSystemFont,
               "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}
</style>
""", unsafe_allow_html=True)

# ==================== LOGIN PAGE ====================
def show_login():
    col = st.columns([1, 2, 1])[1]
    with col:
        st.title("🔐 Better PESU Acad")
        st.caption("Login with Firebase")
        
        st.divider()
        
        # Tab selection
        tab1, tab2, tab3 = st.tabs(["Login", "Sign Up", "Reset Password"])
        
        with tab1:
            st.subheader("Login to Your Account")
            
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="you@example.com", key="login_email")
                password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")
                
                submitted = st.form_submit_button("Login", type="primary", use_container_width=True)

            if submitted:
                if not email or not password:
                    st.error("❌ Please enter both email and password")
                else:
                    with st.spinner("Authenticating..."):
                        result = sign_in(email, password)
                    
                    if result["success"]:
                        st.session_state.authenticated = True
                        st.session_state.user_email = result["email"]
                        st.session_state.user_id = result["user_id"]
                        st.session_state.id_token = result["id_token"]
                        st.session_state.current_page = 'dashboard'
                        st.success("✅ Login successful!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ {result['error']}")
        
        with tab2:
            st.subheader("Create a New Account")
            
            with st.form("signup_form"):
                name = st.text_input("Full Name", placeholder="John Doe", key="signup_name")
                email = st.text_input("Email", placeholder="you@example.com", key="signup_email")
                branch = st.selectbox("Branch", ["CSE", "AIML", "ECE", "BT", "EEE", "ME"], key="signup_branch")
                password = st.text_input("Password", type="password", placeholder="Min 6 characters", key="signup_password")
                password_confirm = st.text_input("Confirm Password", type="password", placeholder="Confirm password", key="signup_confirm")
                
                submitted = st.form_submit_button("Sign Up", type="primary", use_container_width=True)

            if submitted:
                if not name or not email or not branch or not password or not password_confirm:
                    st.error("❌ Please fill in all fields")
                elif password != password_confirm:
                    st.error("❌ Passwords don't match")
                elif len(password) < 6:
                    st.error("❌ Password must be at least 6 characters")
                else:
                    with st.spinner("Creating account..."):
                        result = sign_up(email, password)
                        if result["success"]:
                            st.session_state.user_name = name
                            st.session_state.user_branch = branch
                    
                    if result["success"]:
                        st.session_state.authenticated = True
                        st.session_state.user_email = result["email"]
                        st.session_state.user_id = result["user_id"]
                        st.session_state.id_token = result["id_token"]
                        st.session_state.current_page = 'dashboard'
                        st.success("✅ Account created and logged in!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ {result['error']}")
        
        with tab3:
            st.subheader("Reset Your Password")
            
            if 'reset_step' not in st.session_state:
                st.session_state.reset_step = 1
            
            # STEP 1: Request Reset
            if st.session_state.reset_step == 1:
                st.write("Step 1️⃣: Enter your email")
                
                with st.form("request_reset_form"):
                    email = st.text_input("Email", placeholder="your@example.com", key="reset_email_1")
                    submitted = st.form_submit_button("Send Reset Link", type="primary", use_container_width=True)
                
                if submitted:
                    if not email:
                        st.error("❌ Please enter your email address")
                    else:
                        with st.spinner("Sending reset email..."):
                            result = send_password_reset(email)
                        
                        if result["success"]:
                            st.session_state.reset_email = email
                            st.session_state.reset_step = 2
                            st.success(f"✅ {result['message']}")
                            st.info("📧 Check your email for reset code")
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error(f"❌ {result['error']}")
            
            # STEP 2: Enter Code
            elif st.session_state.reset_step == 2:
                st.write(f"Step 2️⃣: Enter code from email")
                st.info(f"📧 Reset sent to: **{st.session_state.reset_email}**")
                
                with st.form("code_form"):
                    reset_code = st.text_input("Reset Code", placeholder="Paste code from email")
                    col1, col2 = st.columns(2)
                    with col1:
                        submitted = st.form_submit_button("Continue", type="primary", use_container_width=True)
                    with col2:
                        back = st.form_submit_button("← Back")
                
                if back:
                    st.session_state.reset_step = 1
                    st.rerun()
                
                if submitted:
                    if not reset_code:
                        st.error("❌ Please enter the code")
                    else:
                        st.session_state.reset_code = reset_code
                        st.session_state.reset_step = 3
                        time.sleep(1)
                        st.rerun()
            
            # STEP 3: New Password
            elif st.session_state.reset_step == 3:
                st.write(f"Step 3️⃣: Set new password")
                
                with st.form("new_password_form"):
                    new_password = st.text_input("New Password", type="password", placeholder="Min 6 characters")
                    confirm_password = st.text_input("Confirm Password", type="password")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        submitted = st.form_submit_button("Reset Password", type="primary", use_container_width=True)
                    with col2:
                        back = st.form_submit_button("← Back")
                
                if back:
                    st.session_state.reset_step = 2
                    st.rerun()
                
                if submitted:
                    if not new_password or not confirm_password:
                        st.error("❌ Please fill both fields")
                    elif len(new_password) < 6:
                        st.error("❌ Password must be 6+ characters")
                    elif new_password != confirm_password:
                        st.error("❌ Passwords don't match")
                    else:
                        with st.spinner("Resetting password..."):
                            result = confirm_password_reset(st.session_state.reset_code, new_password)
                        
                        if result["success"]:
                            st.success("✅ Password reset successfully!")
                            st.balloons()
                            time.sleep(2)
                            st.session_state.reset_step = 1
                            st.session_state.reset_email = None
                            st.session_state.reset_code = None
                            st.rerun()
                        else:
                            st.error(f"❌ {result['error']}")
        
        st.divider()
        st.caption("🔒 Your data is secured with Firebase Authentication")

# ==================== DASHBOARD PAGE ====================
def show_dashboard():
    # Get local system time
    current_time = datetime.now().astimezone()
    current_hour = current_time.hour
    if current_hour < 12:
        greeting = "Good morning"
    elif current_hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"
    
    st.title(greeting)
    
    # Tasks class
    class ToDoList:
        def __init__(self, tasks_list):
            self.tasks = tasks_list
        
        def add_task(self, task):
            self.tasks.append(task)
        
        def remove_task(self, task):
            if task in self.tasks:
                self.tasks.remove(task)
        
        def finish_task(self, task):
            if task in self.tasks:
                self.tasks.remove(task)
                st.success(f"✅ Done! '{task}' 🎉")
        
        def get_tasks(self):
            return self.tasks
    
    todo_list = ToDoList(st.session_state.tasks)
    
    st.header("✅ Tasks")
    
    with st.expander("Add a Task", expanded=False):
        task_input = st.text_input("Task", placeholder="What do you need to do?", key="task_input_main")
        if st.button("Add Task"):
            if task_input.strip():
                todo_list.add_task(task_input.strip())
                st.rerun()
            else:
                st.warning("Please enter a task!")
    
    if todo_list.get_tasks():
        for task in todo_list.get_tasks():
            col1, col2 = st.columns([0.85, 0.15])
            with col1:
                st.write(f"• {task}")
            with col2:
                if st.button("✓", key=f"finish_{task}"):
                    todo_list.finish_task(task)
                    st.rerun()
    else:
        st.info("No tasks yet! Add one to get started 👆")
    
    st.divider()
    st.caption("Made with ❤️ - Better PESU Acad")

# ==================== COURSES PAGE ====================
def show_courses():
    st.title("📚 Course Materials")
    st.caption("Share & manage course materials organized by subject")
    
    user_email = st.session_state.get('user_email', 'Unknown')
    
    st.markdown("---")
    st.subheader("📤 Upload Materials")
    st.caption("Upload course materials to share with others")
    
    with st.form("upload_materials", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            course_code = st.text_input("Course Code", placeholder="UE22CS202", help="e.g., UE22CS202", key="course_code_main")
        
        with col2:
            course_title = st.text_input("Course Title", placeholder="Data Structures", help="e.g., Data Structures", key="course_title_main")
        
        files = st.file_uploader("Upload files", accept_multiple_files=True, help="Select one or more files to upload", key="files_main")
        
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
                            storage_path = f"course_materials/{course_code.strip()}/{uploaded_file.name}"
                            
                            public_url = upload_to_github(
                                uploaded_file.getvalue(), 
                                storage_path, 
                                commit_message=f"Upload {course_code.strip()}: {uploaded_file.name}"
                            )
                            
                            add_material(
                                course_code=course_code.strip(),
                                course_title=course_title.strip(),
                                filename=uploaded_file.name,
                                file_url=public_url,
                                section=None,
                                uploaded_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                uploaded_by=user_email
                            )
                    
                    st.success(f"✅ Successfully uploaded {len(files)} file(s)!")
                    
                except Exception as e:
                    st.error(f"Upload failed: {str(e)}")
    
    st.markdown("---")
    st.subheader("📚 Available Materials")
    
    try:
        materials = get_materials_by_section(None, None)
        
        if not materials:
            st.info("No materials uploaded yet. Be the first to share! 🚀")
        else:
            materials_by_course = {}
            for material in materials:
                course_code = material.get("course_code", "Unknown")
                if course_code not in materials_by_course:
                    materials_by_course[course_code] = []
                materials_by_course[course_code].append(material)
            
            for course_code in sorted(materials_by_course.keys()):
                course_materials = materials_by_course[course_code]
                course_title = course_materials[0].get("course_title", course_code)
                
                with st.expander(f"📘 {course_code} - {course_title}", expanded=False):
                    course_materials = sorted(course_materials, key=lambda x: x.get("uploaded_at", ""), reverse=True)
                    
                    for i, material in enumerate(course_materials):
                        col1, col2 = st.columns([4, 1])
                        
                        with col1:
                            filename = material.get("filename", "file")
                            uploaded_at = material.get("uploaded_at", "Unknown date")
                            file_url = material.get("file_url")
                            
                            st.markdown(f"**📄 {filename}**")
                            st.caption(f"Uploaded: {uploaded_at}")
                            
                            if file_url:
                                st.link_button("View File", file_url, type="primary", use_container_width=True)
                        
                        with col2:
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

# ==================== SETTINGS PAGE ====================
def show_settings():
    st.title("⚙️ Settings")
    st.caption("Manage your profile and account")
    
    st.markdown("---")
    st.subheader("👤 Profile Information")
    
    # Display user profile info in a nice format
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Full Name", st.session_state.user_name or "Not set")
    with col2:
        st.metric("Branch", st.session_state.user_branch or "Not set")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Email", st.session_state.user_email or "Not set")
    with col2:
        st.metric("User ID", st.session_state.user_id[:8] + "..." if st.session_state.user_id else "Not set")
    
    st.markdown("---")
    st.subheader("🔒 Account")
    
    if st.button("🚪 Logout", type="secondary", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user_email = None
        st.session_state.user_name = None
        st.session_state.user_branch = None
        st.session_state.user_id = None
        st.session_state.id_token = None
        st.session_state.current_page = 'login'
        st.success("✅ Logged out successfully!")
        time.sleep(1)
        st.rerun()
    
    st.divider()
    st.caption("Made with ❤️ - Better PESU Acad")

# ==================== MAIN ROUTING ====================
if not st.session_state.authenticated:
    show_login()
else:
    # Sidebar for authenticated users
    with st.sidebar:
        st.caption(f"**{st.session_state.user_email}**")
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 Dashboard", use_container_width=True):
                st.session_state.current_page = 'dashboard'
                st.rerun()
        with col2:
            if st.button("📚 Courses", use_container_width=True):
                st.session_state.current_page = 'courses'
                st.rerun()
        
        st.divider()
        if st.button("Logout", type="secondary", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_email = None
            st.session_state.user_id = None
            st.session_state.id_token = None
            st.session_state.current_page = 'login'
            st.rerun()
    
    # Show current page
    if st.session_state.current_page == 'dashboard':
        show_dashboard()
    elif st.session_state.current_page == 'courses':
        show_courses()