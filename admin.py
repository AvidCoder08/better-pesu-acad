import streamlit as st
from datetime import datetime
from session_utils import restore_session_from_cookie
from role_utils import is_cr, get_class_id, get_user_ids
from firebase_utils import get_firestore_client
from google_drive_utils import get_drive_service, create_folder_if_not_exists, upload_file_correct, delete_file, list_files_in_folder

restore_session_from_cookie()

if not st.session_state.get('logged_in', False):
    st.warning("⚠️ Please login first")
    st.page_link("login.py", label="Go to Login", icon="🔐")
    st.stop()

profile = st.session_state.profile
if not is_cr(profile):
    st.error("You do not have access to this page.")
    st.stop()

st.title("👩‍💼 Class Admin")
st.caption("Upload teacher-provided materials for your class")

try:
    db = get_firestore_client()
    drive_service = get_drive_service()
except Exception as exc:
    st.error(f"Firebase or Google Drive not configured: {exc}")
    st.stop()

class_id = get_class_id(profile)
user_ids = get_user_ids(profile)

st.info(f"Class ID: {class_id}")

st.subheader("Upload Materials")
with st.form("upload_teacher_materials"):
    course_code = st.text_input("Course Code", placeholder="UE22CS202")
    course_title = st.text_input("Course Title", placeholder="Data Structures")
    visibility = st.selectbox("Visibility", ["Class Only"], index=0, disabled=True)
    files = st.file_uploader("Upload files", accept_multiple_files=True)
    submit = st.form_submit_button("Upload", type="primary")

    if submit:
        if not course_code.strip():
            st.error("Course code is required")
        elif not files:
            st.error("Please select at least one file")
        else:
            try:
                root_folder_id = create_folder_if_not_exists(drive_service, "Hail Mary - Teacher Materials")
                class_folder_id = create_folder_if_not_exists(drive_service, class_id, parent_id=root_folder_id)
                course_folder_id = create_folder_if_not_exists(drive_service, course_code.strip(), parent_id=class_folder_id)
                
                for uploaded in files:
                    file_id, drive_link = upload_file_correct(drive_service, uploaded.getvalue(), uploaded.name, course_folder_id)
                    
                    doc = {
                        "class_id": class_id,
                        "course_code": course_code.strip(),
                        "course_title": course_title.strip(),
                        "filename": uploaded.name,
                        "drive_file_id": file_id,
                        "drive_link": drive_link,
                        "content_type": uploaded.type,
                        "size": uploaded.size,
                        "uploaded_by": next(iter(user_ids)) if user_ids else "unknown",
                        "uploaded_at": datetime.utcnow().isoformat(),
                    }
                    db.collection("teacher_materials").add(doc)
                st.success("Upload complete")
            except Exception as exc:
                st.error(f"Upload failed: {exc}")

st.divider()
st.subheader("Existing Class Materials")

materials = []
for doc in db.collection("teacher_materials").where("class_id", "==", class_id).stream():
    data = doc.to_dict() or {}
    data["id"] = doc.id
    materials.append(data)

if not materials:
    st.info("No materials uploaded yet.")
else:
    materials = sorted(materials, key=lambda x: x.get("uploaded_at", ""), reverse=True)
    for item in materials:
        title = item.get("course_title") or item.get("course_code") or "Course"
        filename = item.get("filename", "file")
        with st.expander(f"{title} • {filename}"):
            st.write(f"Course: {item.get('course_code', '')}")
            st.write(f"Uploaded at: {item.get('uploaded_at', '')}")
            drive_link = item.get("drive_link")
            if drive_link:
                st.link_button("Open in Google Drive", drive_link, type="primary")
            else:
                st.error("Drive link unavailable")
            if st.button("Delete", key=f"delete_{item['id']}"):
                try:
                    delete_file(drive_service, item.get("drive_file_id"))
                except Exception:
                    pass
                db.collection("teacher_materials").document(item["id"]).delete()
                st.success("Deleted")
                st.rerun()
