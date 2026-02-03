import streamlit as st
import datetime as dt
from datetime import date
from session_utils import restore_session_from_cookie
from firebase_utils import get_firestore_client
from role_utils import is_superadmin

restore_session_from_cookie()

# Check if user is logged in
if not st.session_state.get('logged_in', False):
    st.warning("⚠️ Yo, gotta log in first no cap 🔐")
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
            st.success(f"✅ Yessir! '{task}' is done fr fr 🔥")

    def get_tasks(self):
        return self.tasks

todo_list = ToDoList(st.session_state.tasks)

# Academic Calendar Section
st.divider()
st.header("📅 Academic Calendar")
st.caption("Managed by the GOAT (superadmin) 🐐")

if is_superadmin(profile):
    st.page_link("superadmin.py", label="Manage Calendar", icon="🛡️")

def _parse_date(value):
    try:
        return date.fromisoformat(value) if value else None
    except Exception:
        return None

events = []
try:
    db = get_firestore_client()
    for doc in db.collection("calendar_events").stream():
        data = doc.to_dict() or {}
        events.append({
            "id": doc.id,
            "title": data.get("title", "Untitled"),
            "type": data.get("type", "milestone"),
            "start_date": _parse_date(data.get("start_date")),
            "end_date": _parse_date(data.get("end_date")),
            "description": data.get("description", ""),
        })
except Exception as exc:
    st.error(f"Calendar is down fr 💔 {exc}")
    events = []

if not events:
    st.info("No events yet bestie! Dead asf 💀")
else:
    today = date.today()
    upcoming = [e for e in events if (e.get("end_date") or e.get("start_date") or today) >= today]
    upcoming = sorted(upcoming, key=lambda x: x.get("start_date") or today)

    st.subheader("🔔 Upcoming")
    for event in upcoming[:6]:
        start = event.get("start_date")
        end = event.get("end_date")
        title = event.get("title")
        event_type = event.get("type")

        if start and end:
            date_str = f"{start.strftime('%b %d')} - {end.strftime('%b %d, %Y')}"
            days_until = (start - today).days
        elif start:
            date_str = start.strftime("%B %d, %Y")
            days_until = (start - today).days
        else:
            date_str = "Date TBD"
            days_until = None

        icon = {
            "holiday": "🎉",
            "assessment": "📝",
            "meeting": "👥",
            "milestone": "📍",
        }.get(event_type, "📍")

        card = st.container(border=True)
        col_icon, col_text = card.columns([1, 9])
        with col_icon:
            st.markdown(f"<h1 style='text-align: center;'>{icon}</h1>", unsafe_allow_html=True)
        with col_text:
            st.markdown(f"**{title}**")
            if days_until is None:
                st.caption(date_str)
            elif days_until == 0:
                st.caption(f"{date_str} • **Today!**")
            elif days_until == 1:
                st.caption(f"{date_str} • Tomorrow")
            elif days_until < 7:
                st.caption(f"{date_str} • In {days_until} days")
            else:
                st.caption(date_str)

            if event.get("description"):
                st.caption(event.get("description"))

    with st.expander("📆 Full Calendar"):
        events_sorted = sorted(events, key=lambda x: x.get("start_date") or today)
        for event in events_sorted:
            start = event.get("start_date")
            end = event.get("end_date")
            title = event.get("title")
            event_type = event.get("type")

            if start and end:
                date_str = f"{start.strftime('%b %d')} - {end.strftime('%b %d, %Y')}"
            elif start:
                date_str = start.strftime("%B %d, %Y")
            else:
                date_str = "Date TBD"

            st.write(f"• **{title}** ({event_type}) — {date_str}")