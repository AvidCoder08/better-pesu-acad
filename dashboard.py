import streamlit as st
from datetime import datetime
from session_utils import restore_session_from_cookie

restore_session_from_cookie()

# Get local system time with timezone awareness
current_time = datetime.now().astimezone()

# Get time-based greeting
current_hour = current_time.hour
if current_hour < 12:
    greeting = "Good morning"
elif current_hour < 18:
    greeting = "Good afternoon"
else:
    greeting = "Good evening"

st.title(greeting)

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