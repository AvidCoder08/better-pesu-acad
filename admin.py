import streamlit as st
from datetime import datetime
from session_utils import restore_session_from_cookie
from role_utils import is_cr, get_class_id, get_user_ids
from firebase_utils import get_firestore_client, upload_to_storage, delete_from_storage

restore_session_from_cookie()

if not st.session_state.get('logged_in', False):
    st.warning("⚠️ Yo, gotta log in first no cap 🔐")
    st.page_link("login.py", label="Go to Login", icon="🔐")
    st.stop()

profile = st.session_state.profile
if not is_cr(profile):
    st.error("Nah you ain't got permission for this bestie 🚫")
    st.stop()

st.title("👩‍💼 Class Admin")
st.caption("Upload teacher files so ur class eats 📚✨")

try:
    db = get_firestore_client()
except Exception as exc:
    st.error(f"Backend is acting up ngl 💔 {exc}")
    st.stop()

class_id = get_class_id(profile)
user_ids = get_user_ids(profile)

st.info(f"Your class: {class_id} 🏫")

st.subheader("Upload Materials")
with st.form("upload_teacher_materials"):
    course_code = st.text_input("Course Code", placeholder="UE22CS202")
    course_title = st.text_input("Course Title", placeholder="Data Structures")
    visibility = st.selectbox("Visibility", ["Class Only"], index=0, disabled=True)
    files = st.file_uploader("Upload files", accept_multiple_files=True)
    submit = st.form_submit_button("Upload", type="primary")

    if submit:
        if not course_code.strip():
            st.error("We need that course code bestie! 📝")
        elif not files:
            st.error("Pick at least one file fr fr 📁")
        else:
            try:
                for uploaded in files:
                    storage_path = f"teacher_materials/{class_id}/{course_code.strip()}/{uploaded.name}"
                    public_url = upload_to_storage(uploaded.getvalue(), storage_path, uploaded.type or "application/octet-stream")
                    
                    doc = {
                        "class_id": class_id,
                        "course_code": course_code.strip(),
                        "course_title": course_title.strip(),
                        "filename": uploaded.name,
                        "storage_path": storage_path,
                        "file_url": public_url,
                        "content_type": uploaded.type,
                        "size": uploaded.size,
                        "uploaded_by": next(iter(user_ids)) if user_ids else "unknown",
                        "uploaded_at": datetime.utcnow().isoformat(),
                    }
                    db.collection("teacher_materials").add(doc)
                st.success("Uploaded fr! Your class eats now 🔥")
            except Exception as exc:
                st.error(f"Upload ghosted us ngl 👻 {exc}")

st.divider()
st.subheader("Existing Class Materials")

materials = []
for doc in db.collection("teacher_materials").where("class_id", "==", class_id).stream():
    data = doc.to_dict() or {}
    data["id"] = doc.id
    materials.append(data)

if not materials:
    st.info("No materials yet! Upload sum fr 📚")
else:
    materials = sorted(materials, key=lambda x: x.get("uploaded_at", ""), reverse=True)
    for item in materials:
        title = item.get("course_title") or item.get("course_code") or "Course"
        filename = item.get("filename", "file")
        with st.expander(f"{title} • {filename}"):
            st.write(f"Course: {item.get('course_code', '')}")
            st.write(f"Uploaded at: {item.get('uploaded_at', '')}")
            file_url = item.get("file_url")
            if file_url:
                st.link_button("Open File", file_url, type="primary")
            else:
                st.error("File link unavailable")
            if st.button("Delete", key=f"delete_{item['id']}"):
                try:
                    storage_path = item.get("storage_path")
                    if storage_path:
                        delete_from_storage(storage_path)
                except Exception:
                    pass
                db.collection("teacher_materials").document(item["id"]).delete()
                st.success("Yeeted that file 🗑️")
                st.rerun()
