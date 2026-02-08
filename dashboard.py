import streamlit as st
from session_utils import restore_session_from_cookie

restore_session_from_cookie()

# Get profile data
profile = st.session_state.profile

# Handle both dict and object profiles
if profile is None:
    name = 'User'
    program = 'N/A'
    branch = 'N/A'
    semester = 'N/A'
elif isinstance(profile, dict):
    personal = profile.get('personal', {})
    name = personal.get('name', 'User') if isinstance(personal, dict) else personal.get('name', 'User')
    program = personal.get('program', 'N/A') if isinstance(personal, dict) else personal.get('program', 'N/A')
    branch = personal.get('branch', 'N/A') if isinstance(personal, dict) else personal.get('branch', 'N/A')
    semester = personal.get('semester', 'N/A') if isinstance(personal, dict) else personal.get('semester', 'N/A')
else:
    personal = profile.personal if hasattr(profile, 'personal') else None
    if personal:
        name = personal.name if hasattr(personal, 'name') else 'User'
        program = personal.program if hasattr(personal, 'program') else 'N/A'
        branch = personal.branch if hasattr(personal, 'branch') else 'N/A'
        semester = personal.semester if hasattr(personal, 'semester') else 'N/A'
    else:
        name = 'User'
        program = 'N/A'
        branch = 'N/A'
        semester = 'N/A'

st.title("Dashboard")

# Initialize session state for tasks
if 'tasks' not in st.session_state:
    st.session_state.tasks = []

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

# Tasks Section
st.header("✅ Tasks")

with st.expander("Add a Task", expanded=False):
    task_input = st.text_input("Task", placeholder="What do you need to do?")
    if st.button("Add Task"):
        if task_input.strip():
            todo_list.add_task(task_input.strip())
            st.rerun()
        else:
            st.warning("Please enter a task!")

# Display tasks
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