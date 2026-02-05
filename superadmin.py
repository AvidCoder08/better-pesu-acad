import streamlit as st
from datetime import date
from session_utils import restore_session_from_cookie
from firebase_utils import get_firestore_client
from role_utils import is_superadmin

restore_session_from_cookie()

if not st.session_state.get('logged_in', False):
    st.warning("⚠️ Yo, gotta log in first no cap 🔐")
    st.page_link("login.py", label="Go to Login", icon="🔐")
    st.stop()

profile = st.session_state.profile
if not is_superadmin(profile):
    st.error("Nah you ain't got permission for this bestie 🚫")
    st.stop()

st.title("🛡️ Superadmin")
st.caption("U da GOAT - manage everything 🐐✨")

try:
    db = get_firestore_client()
except Exception as exc:
    st.error(f"Firebase said nope 🚫 {exc}")
    st.stop()

st.subheader("Create Calendar Event")
with st.form("create_event_form", clear_on_submit=True):
    title = st.text_input("Title", placeholder="ISA 1 WEEK (Units I & II)")
    event_type = st.selectbox("Type", ["assessment", "meeting", "holiday", "milestone"], index=0)
    start_date = st.date_input("Start date", value=date.today())
    has_end_date = st.checkbox("Has end date", value=False)
    end_date = st.date_input("End date", value=date.today()) if has_end_date else None
    description = st.text_area("Description (optional)", placeholder="Any additional notes")

    submitted = st.form_submit_button("Add Event", type="primary")
    if submitted:
        if not title.strip():
            st.error("Gotta give this event a name bestie! 📛")
        else:
            payload = {
                "title": title.strip(),
                "type": event_type,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat() if end_date else None,
                "description": description.strip() if description else "",
            }
            db.collection("calendar_events").add(payload)
            st.success("Event is live! Go off sis 🎉")
            st.rerun()

st.divider()
st.subheader("Existing Events")

try:
    events = []
    for doc in db.collection("calendar_events").stream():
        data = doc.to_dict() or {}
        data["id"] = doc.id
        events.append(data)

    def sort_key(item):
        return item.get("start_date", "") or ""

    events = sorted(events, key=sort_key)

    if not events:
        st.info("No events bestie! Add sum 📅")
    else:
        for event in events:
            title = event.get("title", "Untitled")
            start = event.get("start_date") or ""
            end = event.get("end_date") or ""
            event_type = event.get("type", "")
            description = event.get("description", "")

            with st.expander(f"{title} ({event_type})"):
                st.write(f"Start: {start}")
                if end:
                    st.write(f"End: {end}")
                if description:
                    st.caption(description)

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Delete", key=f"delete_{event['id']}"):
                        db.collection("calendar_events").document(event["id"]).delete()
                        st.success("Yeeted that event 🗑️")
                        st.rerun()
                with col2:
                    with st.form(f"edit_{event['id']}"):
                        new_title = st.text_input("Title", value=title)
                        new_type = st.selectbox(
                            "Type",
                            ["assessment", "meeting", "holiday", "milestone"],
                            index=["assessment", "meeting", "holiday", "milestone"].index(event_type) if event_type in ["assessment", "meeting", "holiday", "milestone"] else 0,
                        )
                        new_start = st.date_input("Start date", value=date.fromisoformat(start) if start else date.today())
                        has_end = st.checkbox("Has end date", value=bool(end), key=f"has_end_{event['id']}")
                        new_end = st.date_input("End date", value=date.fromisoformat(end) if end else date.today()) if has_end else None
                        new_desc = st.text_area("Description", value=description)
                        saved = st.form_submit_button("Save Changes")
                        if saved:
                            updated = {
                                "title": (new_title or "").strip(),
                                "type": new_type,
                                "start_date": new_start.isoformat(),
                                "end_date": new_end.isoformat() if new_end else None,
                                "description": (new_desc or "").strip(),
                            }
                            db.collection("calendar_events").document(event["id"]).set(updated)
                            st.success("Updated fr fr! 🔥")
                            st.rerun()
except Exception as exc:
    st.error(f"Couldn't load events ngl 😪 {exc}")
