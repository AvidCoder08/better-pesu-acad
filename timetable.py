import streamlit as st
import asyncio
from pesuacademy import PESUAcademy
from session_utils import restore_session_from_cookie

restore_session_from_cookie()

if not st.session_state.get('logged_in', False):
    st.warning("⚠️ Yo, gotta log in first no cap 🔐")
    st.page_link("login.py", label="Go to Login", icon="🔐")
    st.stop()

st.title("📅 Your Schedule (No Skipping!)")
st.caption("Your weekly timetable fr fr 💯")

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

if st.button("🔄 Load Schedule", type="primary", use_container_width=True):
    with st.spinner("Loading ur schedule... 👀"):
        timetable, error = asyncio.run(fetch_timetable())
        
        if error:
            st.error(f"Bruh that didn't work 💔 {error}")
        elif timetable:
            st.session_state.timetable = timetable
            st.success("Schedule loaded bestie! 🎉")
        else:
            st.error("No timetable data fr")

if 'timetable' in st.session_state and st.session_state.timetable:
    timetable = st.session_state.timetable
    
    # Days of the week
    days_order = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
    days_display = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    
    st.divider()
    st.subheader("📋 Weekly Schedule")
    
    for day_idx, (day_key, day_display) in enumerate(zip(days_order, days_display)):
        if day_key in timetable.days and timetable.days[day_key]:
            with st.expander(f"📍 {day_display}", expanded=(day_idx == 0)):
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
    st.info("👆 Click 'Load Schedule' to see ur weekly schedule bestie! 📚")
