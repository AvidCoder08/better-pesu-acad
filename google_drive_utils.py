import os
import streamlit as st
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO


SCOPES = ["https://www.googleapis.com/auth/drive"]


def _load_credentials():
    if "google_drive_service_account" in st.secrets:
        creds_dict = dict(st.secrets["google_drive_service_account"])
        return Credentials.from_service_account_info(creds_dict, scopes=SCOPES)

    service_account_path = os.getenv("GOOGLE_DRIVE_SERVICE_ACCOUNT")
    if service_account_path and os.path.exists(service_account_path):
        return Credentials.from_service_account_file(service_account_path, scopes=SCOPES)

    raise RuntimeError(
        "Google Drive credentials not found. Set st.secrets['google_drive_service_account'] or GOOGLE_DRIVE_SERVICE_ACCOUNT."
    )


def get_drive_service():
    try:
        creds = _load_credentials()
    except Exception:
        raise RuntimeError(
            "Google Drive authentication failed. Check your credentials setup."
        )
    return build("drive", "v3", credentials=creds)


def create_folder_if_not_exists(service, folder_name, parent_id=None):
    """Create a folder in Google Drive if it doesn't exist, return folder ID."""
    try:
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        if parent_id:
            query += f" and '{parent_id}' in parents"
        
        results = service.files().list(q=query, spaces="drive", fields="files(id, name)", pageSize=1).execute()
        files = results.get("files", [])
        
        if files:
            return files[0]["id"]
        
        file_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
        }
        if parent_id:
            file_metadata["parents"] = [parent_id]
        
        folder = service.files().create(body=file_metadata, fields="id").execute()
        return folder.get("id")
    except HttpError as error:
        raise RuntimeError(f"Google Drive error: {error}")


def upload_file_correct(service, file_bytes, filename, parent_folder_id):
    """Upload file bytes to Google Drive."""
    try:
        file_metadata = {
            "name": filename,
            "parents": [parent_folder_id],
        }
        
        stream = BytesIO(file_bytes)
        media = MediaIoBaseUpload(stream, mimetype="application/octet-stream", resumable=False)
        
        file_obj = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id, webViewLink"
        ).execute()
        
        return file_obj.get("id"), file_obj.get("webViewLink")
    except HttpError as error:
        raise RuntimeError(f"Upload failed: {error}")


def delete_file(service, file_id):
    """Delete a file from Google Drive."""
    try:
        service.files().delete(fileId=file_id).execute()
    except HttpError as error:
        raise RuntimeError(f"Delete failed: {error}")


def list_files_in_folder(service, folder_id):
    """List all files in a folder."""
    try:
        results = service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            spaces="drive",
            fields="files(id, name, mimeType, createdTime)",
            pageSize=100
        ).execute()
        return results.get("files", [])
    except HttpError as error:
        raise RuntimeError(f"List failed: {error}")
