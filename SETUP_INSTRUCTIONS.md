# Better PESU Acad - Setup Instructions

A streamlined educational platform with Firebase authentication, course material sharing via GitHub, and task management.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Firebase Setup](#firebase-setup)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Adding Authorized Friends](#adding-authorized-friends)
6. [Running the App](#running-the-app)
7. [Usage Guide](#usage-guide)
8. [Troubleshooting](#troubleshooting)

---

## 📦 Prerequisites

Before you start, ensure you have:

- **Python 3.8+** installed
- **Git** installed
- A **Firebase Project** (create one at [firebase.google.com](https://firebase.google.com))
- A **GitHub account** with a repository for storing materials
- Basic understanding of command line/terminal

---

## 🔥 Firebase Setup

### Step 1: Create a Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Click **"Add project"**
3. Name it (e.g., "Better PESU Acad")
4. Click **"Create project"** and wait for completion

### Step 2: Set Up Firestore Database

1. In Firebase Console, go to **Firestore Database**
2. Click **"Create database"**
3. Choose **"Start in production mode"**
4. Select your preferred location
5. Click **"Create"**

### Step 3: Create Friends Collection

1. In Firestore, click **"+ Start collection"**
2. Collection name: `friends`
3. Document ID: `allowed_emails`
4. Click **"Next"**
5. Add a field:
   - Field name: `emails`
   - Type: `array`
   - Values (click **"Add array element"** for each):
     - `your_email@gmail.com`
     - `friend1@gmail.com`
     - `friend2@gmail.com`
6. Click **"Save"**

### Step 4: Get Firebase Credentials

1. Go to **Project Settings** (⚙️ icon, top right)
2. Click the **"Service accounts"** tab
3. Click **"Generate new private key"**
4. A JSON file will download - **keep it safe!**
5. Copy the entire content of this JSON file

---

## 💻 Installation

### Step 1: Clone/Download the Project

```bash
cd c:\Users\soham\Developer\better-pesu-acad
```

### Step 2: Create Virtual Environment (Optional but Recommended)

```bash
# On Windows with PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

If you get an error about `pesuacademy-dev`, you can ignore it or remove that line from `requirements.txt`:

```bash
pip install streamlit toml st-theme lxml python-dotenv requests cryptography extra-streamlit-components firebase-admin
```

---

## ⚙️ Configuration

### Step 1: Create `.streamlit/secrets.toml`

Create a new file at `.streamlit/secrets.toml` in your project root:

```toml
# Firebase Service Account JSON (paste the content from Step 4 above)
firebase_service_account_json = '''
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "...",
  ...
}
'''

# Firebase Storage Bucket (optional, if you use Firebase Storage)
firebase_storage_bucket = "your-project-id.appspot.com"
```

**OR** Create `.env` file:

```env
FIREBASE_SERVICE_ACCOUNT_JSON={"type": "service_account", "project_id": "...", ...}
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
```

### Step 2: Configure GitHub (for Material Uploads)

Create/update `.env` file:

```env
GITHUB_TOKEN=your_github_token_here
GITHUB_REPO=your_username/your_repo_name
GITHUB_BRANCH=main
```

**How to get GitHub Token:**
1. Go to [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
2. Click **"Generate new token"**
3. Select scopes: `repo` (full control of private repositories)
4. Click **"Generate token"** and copy it

---

## 👥 Adding Authorized Friends

### Method 1: Through Firestore Console (Easy)

1. Open [Firebase Console](https://console.firebase.google.com)
2. Go to Firestore → Collection `friends` → Document `allowed_emails`
3. Edit the `emails` array
4. Click **"Add array element"** and type the friend's email
5. Click **"Update"**

### Method 2: Using Python Script

Create a file `add_friend.py`:

```python
from firebase_utils import add_friend_email

# Add a single friend
add_friend_email("friend@gmail.com")
print("Friend added!")

# Add multiple friends
friends = [
    "alice@gmail.com",
    "bob@gmail.com",
    "charlie@gmail.com"
]

for email in friends:
    add_friend_email(email)
    print(f"Added {email}")
```

Run it:
```bash
python add_friend.py
```

### Method 3: Remove a Friend

```python
from firebase_utils import remove_friend_email

remove_friend_email("friend@gmail.com")
```

---

## 🚀 Running the App

### Local Development

```bash
# In your project directory
streamlit run main.py
```

The app will open at `http://localhost:8501`

### Deploy to Streamlit Cloud (Free Option)

1. Push your code to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Click **"New app"**
4. Select your GitHub repo and `main.py`
5. Add secrets in **"Advanced settings"**:
   - Paste your Firebase credentials
   - Add GitHub token

---

## 📖 Usage Guide

### 🔐 Login

1. Open the app
2. Enter your email (must be in friends list)
3. Enter any password (currently not validated)
4. Click **"Login"**
5. You're in! 🎉

### 📊 Dashboard

- See a time-based greeting (Good morning/afternoon/evening)
- Create and manage your to-do tasks
- Click **"Add a Task"** to add items
- Click ✓ to mark tasks complete

### 📚 Course Materials

**Upload Materials:**
1. Enter course code (e.g., `UE22CS202`)
2. Enter course title (e.g., `Data Structures`)
3. Select files to upload (multiple supported)
4. Click **"Upload"**
5. Files will be stored in GitHub and indexed

**View Materials:**
- Materials are grouped by course code
- Click to expand course section
- Click **"View File"** to open materials
- Only you can delete your uploads

### 👤 Profile

- Your email is shown in the sidebar
- Click **"Logout"** to sign out

---

## 🛠️ Troubleshooting

### "Firebase credentials not found"

**Solution:**
- Make sure `.env` file or `.streamlit/secrets.toml` exists
- Copy the exact JSON from Firebase Service Account
- Check for proper formatting (valid JSON)

### "ModuleNotFoundError: No module named 'firebase_admin'"

**Solution:**
```bash
pip install firebase-admin
```

### "Permission denied" on Firestore

**Solution:**
1. Go to Firebase → Firestore → Rules
2. Replace with:
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if true;
    }
  }
}
```
**⚠️ Warning:** This is for development only. Use proper authentication rules for production.

### "Email not in friends list" error

**Solution:**
- Make sure email is exactly as spelled (case-sensitive)
- Add it via Firestore or Python script
- Wait a few seconds for database to sync

### Materials not uploading

**Solution:**
- Check GitHub token is valid
- Verify repository name in `.env`
- Make sure GitHub token has `repo` scope permission

### Time greeting is wrong

**Solution:**
- Set timezone in environment:
  ```bash
  # On Windows PowerShell
  $env:TZ = "Asia/Kolkata"
  
  # On macOS/Linux
  export TZ="Asia/Kolkata"
  ```

---

## 📁 Project Structure

```
better-pesu-acad/
├── main.py                 # Main app entry point (authentication)
├── pages/
│   ├── login.py           # Login page
│   ├── dashboard.py       # Dashboard & tasks
│   └── courses.py         # Material sharing
├── firebase_utils.py      # Firebase helper functions
├── github_utils.py        # GitHub upload/delete
├── materials_utils.py     # Material database logic
├── session_utils.py       # Session management
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
└── .streamlit/
    └── secrets.toml       # Streamlit secrets
```

---

## 🔒 Privacy & Security

- **No passwords are validated** - for production, integrate proper Firebase Auth
- **Material access is public** - anyone with the app can see materials
- **Consider adding roles** for different permission levels
- **Use HTTPS** when deployed on production
- **Rotate GitHub tokens** regularly

---

## 📞 Support

If you encounter issues:

1. Check the **Troubleshooting** section above
2. Review Firebase Console for errors
3. Check browser console for JavaScript errors (F12)
4. Check terminal/command line for Python errors

---

## 🎯 Next Steps

1. ✅ Set up Firebase
2. ✅ Configure credentials
3. ✅ Add authorized friends
4. ✅ Run the app
5. 🚀 Deploy to Streamlit Cloud

Enjoy! 🎓
