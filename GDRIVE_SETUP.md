# Google Drive Setup Guide

## Summary
Teacher materials are now stored in **Google Drive** instead of Firebase Storage. The calendar remains in **Firestore**. This is simpler and free.

## Step-by-Step Setup

### 1. Create a Google Cloud Project
- Go to https://console.cloud.google.com/
- Create a new project (name it something like "Hail Mary")

### 2. Enable Google Drive API
- In the Google Cloud Console, go to **APIs & Services** → **Library**
- Search for "Google Drive API"
- Click it and press **Enable**

### 3. Create a Service Account
- Go to **APIs & Services** → **Credentials**
- Click **Create Credentials** → **Service Account**
- Fill in the service account name (e.g., "hail-mary-service")
- Click **Create and Continue**
- Grant it **Editor** role (or just **Drive** role if available)
- Click **Continue** and then **Done**

### 4. Generate a Key
- In the Service Accounts list, click the service account you just created
- Go to **Keys** tab
- Click **Add Key** → **Create new key** → **JSON**
- A JSON file will download. **Save it securely**

### 5. Share a Google Drive Folder with the Service Account
- Open Google Drive
- Create a folder called "Hail Mary - Teacher Materials"
- Right-click → **Share**
- Copy the service account email from the JSON file (looks like `xxx@xxx.iam.gserviceaccount.com`)
- Paste it in the share dialog and grant **Editor** access

### 6. Provide Credentials to Your App

**Option A: Streamlit Secrets (Recommended)**
- Create `.streamlit/secrets.toml` in your project root
- Open the JSON file you downloaded
- Add this to secrets.toml (replace `...` with values from JSON):
```toml
google_drive_service_account = {
  "type" = "service_account",
  "project_id" = "your-project-id",
  "private_key_id" = "xxx",
  "private_key" = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email" = "xxx@xxx.iam.gserviceaccount.com",
  "client_id" = "xxx",
  "auth_uri" = "https://accounts.google.com/o/oauth2/auth",
  "token_uri" = "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url" = "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url" = "xxx"
}
```

**Option B: Environment Variable**
- Set `GOOGLE_DRIVE_SERVICE_ACCOUNT` to the path of your JSON file
- Or set `GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON` to the full JSON content

### 7. Install Dependencies
- Run in terminal: `pip install -r requirements.txt`
- The Google Drive packages are now included

### 8. Test
- Run the Streamlit app
- Navigate to the **Class Admin** page (if you're a CR)
- Try uploading a file
- It should appear in your Google Drive folder

## How It Works

1. **Superadmin** manages calendar in the **Superadmin** page (stored in Firestore)
2. **Class Representatives (CRs)** upload materials in the **Class Admin** page
3. Files are uploaded to Google Drive in this structure:
   ```
   Hail Mary - Teacher Materials/
   ├── BTech-CSE-Sem2-A/
   │   ├── UE22CS202/
   │   │   ├── lecture1.pdf
   │   │   ├── notes.docx
   │   └── UE22CS203/
   │       └── assignment.pdf
   ```
4. **Students** see their class materials in the **Courses** page → **Teacher Files** tab
5. Files are linked directly to Google Drive for easy opening/downloading

## Troubleshooting

- **"Google Drive not configured"**: Check that `google_drive_service_account` is in `.streamlit/secrets.toml` or `GOOGLE_DRIVE_SERVICE_ACCOUNT` env var is set
- **"Permission denied"**: Make sure the service account email has access to the "Hail Mary - Teacher Materials" folder
- **Folder already exists**: The app checks for existing folders and uses them (won't duplicate)

## Dashboard Calendar

The calendar (in the Dashboard) is still managed by the superadmin and stored in **Firestore**. Only you can create/edit events.
