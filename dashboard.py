import streamlit as st
import datetime as dt

# Check if user is logged in
if not st.session_state.get('logged_in', False):
    st.warning("⚠️ Please login first")
    st.page_link("login.py", label="Go to Login", icon="🔐")
    st.stop()

# Get profile data
profile = st.session_state.profile

# Handle both dict and object profiles
if isinstance(profile, dict):
    personal = profile.get('personal', {})
    name = personal.get('name', 'User') if isinstance(personal, dict) else personal.name
    program = personal.get('program', 'N/A') if isinstance(personal, dict) else personal.program
    branch = personal.get('branch', 'N/A') if isinstance(personal, dict) else personal.branch
    section = personal.get('section', 'N/A') if isinstance(personal, dict) else personal.section
    semester = personal.get('semester', 'N/A') if isinstance(personal, dict) else personal.semester
else:
    personal = profile.personal
    name = personal.name
    program = personal.program
    branch = personal.branch
    section = personal.section
    semester = personal.semester

st.title(f"Dashboard - Hi, {name.split()[0]}! 👋")

# Display user info cards
info_col1, info_col2, info_col3 = st.columns(3)
with info_col1:
    st.info(f"**Program:** {program}")
with info_col2:
    st.info(f"**Branch:** {branch}")
with info_col3:
    st.info(f"**Section:** {section} • Sem {semester}")
col1, col2 = st.columns(2)

# Initialize session state for tasks
if 'tasks' not in st.session_state:
    st.session_state.tasks = []

#tasks class
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
            st.success(f"✅'{task}' was completed!")

    def get_tasks(self):
        return self.tasks

todo_list = ToDoList(st.session_state.tasks)

with col1:
    date_c = st.container(border=True,horizontal_alignment="center",vertical_alignment="center",horizontal=True)
    todays_date = dt.date.today().strftime("%d-%m-%Y")
    date_c.header(todays_date)

with col2:
    task_c = st.container(border=True)
    task_c.header("Tasks")
    new_task = task_c.text_input(label="Enter Tasks to complete")
    if task_c.button("Add Task"):
        if new_task:
            todo_list.add_task(new_task)
            task_c.success("Task Added")
        else:
            task_c.error("Please enter task")
    tasks = todo_list.get_tasks()
    for task in tasks:
        if task_c.checkbox(label=task):
            todo_list.finish_task(task)