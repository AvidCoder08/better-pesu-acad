import streamlit as st
import asyncio
from datetime import datetime
from pesuacademy import PESUAcademy
from session_utils import restore_session_from_cookie

restore_session_from_cookie()

if not st.session_state.get('logged_in', False):
    st.warning("⚠️ Yo, gotta log in first no cap 🔐")
    st.page_link("login.py", label="Go to Login", icon="🔐")
    st.stop()

st.title("📅 Your Schedule (No Skipping!)")
st.caption("Your daily & weekly timetable fr fr 💯")

async def fetch_timetable():
    """Fetch timetable from PESU Academy"""
    try:
        pesu = await PESUAcademy.login(
            st.session_state.pesu_username,
            st.session_state.pesu_password
        )
        timetable = await pesu.get_timetable()
        await pesu.close()
        return timetable, None
    except Exception as e:
        return None, str(e)

# Initialize timetable on first load
if 'timetable_initialized' not in st.session_state:
    with st.spinner("Loading ur schedule... 👀"):
        timetable, error = asyncio.run(fetch_timetable())
        
        if error:
            st.error(f"Bruh that didn't work 💔 {error}")
        elif timetable:
            st.session_state.timetable = timetable
            st.session_state.timetable_initialized = True
            st.success("Schedule loaded bestie! 🎉")
        else:
            st.error("No timetable data fr")

if st.button("🔄 Reload Schedule", type="primary", use_container_width=True):
    with st.spinner("Loading ur schedule... 👀"):
        timetable, error = asyncio.run(fetch_timetable())
        
        if error:
            st.error(f"Bruh that didn't work 💔 {error}")
        elif timetable:
            st.session_state.timetable = timetable
            st.success("Schedule reloaded bestie! 🎉")
        else:
            st.error("No timetable data fr")

if 'timetable' in st.session_state and st.session_state.timetable:
    timetable = st.session_state.timetable
    
    # Get today's day name
    today = datetime.now()
    today_day = today.strftime("%A").lower()
    
    # Days of the week
    days_order = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
    days_display = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    
    st.divider()
    st.subheader("📅 Today's Classes")
    
    # Show today's schedule first (always expanded)
    if today_day in timetable.days and timetable.days[today_day]:
        slots = timetable.days[today_day]
        st.markdown(f"**{today.strftime('%A, %B %d, %Y')}**")
        
        has_classes = False
        for slot in slots:
            if slot.is_break:
                st.info(f"⏸️ **Break Time** • {slot.time.start.strftime('%I:%M %p')} - {slot.time.end.strftime('%I:%M %p')}")
            else:
                has_classes = True
                if slot.session:
                    col1, col2 = st.columns([2, 3])
                    with col1:
                        st.markdown(f"**⏰ {slot.time.start.strftime('%I:%M %p')}**")
                        st.caption(f"({slot.time.duration} mins)")
                    with col2:
                        st.markdown(f"**{slot.session.code}**")
                        st.write(f"*{slot.session.name}*")
                        if slot.session.faculty:
                            st.caption(f"👨‍🏫 {slot.session.faculty}")
                    st.divider()
                else:
                    st.info(f"🕐 {slot.time.start.strftime('%I:%M %p')} - Free (no class lol 😎)")
        
        if not has_classes:
            st.info(f"No classes today! Touch grass 🌱")
    else:
        st.info(f"No classes today! Touch grass 🌱")
    
    # Show rest of the week (collapsed)
    st.divider()
    st.subheader("📋 Rest of the Week")
    
    for day_idx, (day_key, day_display) in enumerate(zip(days_order, days_display)):
        # Skip today since we already showed it
        if day_key == today_day:
            continue
            
        if day_key in timetable.days and timetable.days[day_key]:
            with st.expander(f"📍 {day_display}", expanded=False):
                slots = timetable.days[day_key]
                
                for slot in slots:
                    if slot.is_break:
                        st.info(f"⏸️ **Break Time** • {slot.time.start.strftime('%I:%M %p')} - {slot.time.end.strftime('%I:%M %p')}")
                    else:
                        if slot.session:
                            col1, col2 = st.columns([2, 3])
                            with col1:
                                st.markdown(f"**⏰ {slot.time.start.strftime('%I:%M %p')}**")
                                st.caption(f"({slot.time.duration} mins)")
                            with col2:
                                st.markdown(f"**{slot.session.code}**")
                                st.write(f"*{slot.session.name}*")
                                if slot.session.faculty:
                                    st.caption(f"👨‍🏫 {slot.session.faculty}")
                            st.divider()
                        else:
                            st.info(f"🕐 {slot.time.start.strftime('%I:%M %p')} - Free (no class lol 😎)")
        else:
            st.info(f"**{day_display}** - No classes! Touch grass 🌱")
    
    st.divider()
    st.subheader("📊 Schedule Stats")
    
    total_classes = 0
    total_break_time = 0
    
    for day in timetable.days.values():
        for slot in day:
            if not slot.is_break:
                total_classes += 1
            else:
                total_break_time += slot.time.duration
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Classes per Week", total_classes)
    with col2:
        st.metric("Break Time (mins)", total_break_time)
    
    st.info("💡 **Pro Tip:** Save this and never be late to class. Your attendance will thank you fr 🙏")
else:
    st.info("👆 Click 'Reload Schedule' to refresh ur weekly schedule bestie! 📚")
