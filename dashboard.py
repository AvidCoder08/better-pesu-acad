import streamlit as st
import datetime as dt
import python_weather as pw
import asyncio
import time

st.title("Dashboard")
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