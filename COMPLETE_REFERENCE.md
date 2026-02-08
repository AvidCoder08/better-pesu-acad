# Better PESU Acad - Complete Setup Guide

**Version:** 1.0  
**Last Updated:** February 2026  
**Project:** Better PESU Acad - Educational Material Sharing Platform

---

## 📚 Documentation Overview

This package includes:

1. **README.md** - Project overview and features
2. **QUICKSTART.md** - 5-minute setup (new users start here!)
3. **SETUP_INSTRUCTIONS.md** - Detailed step-by-step guide
4. **CONFIGURATION.md** - Configuration examples and troubleshooting
5. **LAUNCH_CHECKLIST.md** - Pre-deployment checklist
6. **THIS FILE** - Complete reference guide

---

## 🎯 Choose Your Path

### 👶 First Time Setup?
→ Read **QUICKSTART.md** (5 min)

### 📖 Want Step-by-Step Instructions?
→ Read **SETUP_INSTRUCTIONS.md**

### ⚙️ Need Configuration Examples?
→ Read **CONFIGURATION.md**

### 🚀 Ready to Deploy?
→ Read **LAUNCH_CHECKLIST.md**

### 📝 Want Everything in One Place?
→ You're reading it now!

---

## 🚀 Super Quick Summary

```bash
# 1. Setup Firebase (5 min)
# - Create project at firebase.google.com
# - Create Firestore DB
# - Add friends collection with emails

# 2. Configure App (2 min)
# - Create .env file
# - Add Firebase JSON
# - Add GitHub credentials

# 3. Run Application (1 min)
pip install -r requirements.txt
streamlit run main.py

# 4. Login
# - Email: your@gmail.com (from friends list)
# - Password: anything (not validated yet)
```

---

## 📋 System Architecture

```
┌─────────────────────────────────────┐
│   Better PESU Acad (Streamlit)      │
├─────────────────────────────────────┤
│                                     │
│  Pages:                             │
│  ├─ Login (Firebase Auth)           │
│  ├─ Dashboard (Tasks)               │
│  └─ Courses (Materials)             │
│                                     │
└─────────────────────────────────────┘
         ↓              ↓
    ┌─────────┐    ┌──────────┐
    │Firebase │    │  GitHub  │
    │Firestore│    │  Storage │
    │ (DB)    │    │  (Files) │
    └─────────┘    └──────────┘
```

---

## 🔐 Firebase Setup

### What You Need

- Firebase account (free at firebase.google.com)
- Your email address

### Step-by-Step

1. **Create Project**
   - Go to firebase.google.com
   - Click "Add project"
   - Name it: "Better PESU Acad"
   - Click "Create project"

2. **Create Firestore Database**
   - Go to Firestore Database
   - Click "Create database"
   - Start in production mode
   - Select location
   - Click "Create"

3. **Create Friends Collection**
   - Collection name: `friends`
   - Document ID: `allowed_emails`
   - Field name: `emails`
   - Field type: `array`
   - Add values: your_email@gmail.com

4. **Get Credentials** ⭐ IMPORTANT
   - Click ⚙️ (Settings)
   - Go to "Service Accounts"
   - Click "Generate New Private Key"
   - Save the JSON file!

5. **Copy JSON Content**
   - Open the downloaded JSON file
   - Copy entire content
   - You'll paste this in .env file

### Firestore Rules (Production)

Go to Firestore → Rules tab:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /friends/allowed_emails {
      allow read: if true;
    }
    match /{document=**} {
      allow read, write: if true;
    }
  }
}
```

Click "Publish"

---

## 🔑 GitHub Setup

### What You Need

- GitHub account (free at github.com)
- A repository for storing materials

### Step-by-Step

1. **Create Repository**
   - Go to github.com
   - Click "New repository"
   - Name: `better-pesu-materials`
   - Make it Public or Private
   - Click "Create repository"

2. **Generate Personal Access Token**
   - Go to github.com/settings/tokens
   - Click "Generate new token"
   - Name: `better-pesu-acad`
   - Expiration: 90 days or longer
   - Scopes: Check `repo` and `read:user`
   - Click "Generate token"
   - **Copy immediately** (won't show again!)

3. **Get Repository Name**
   - Go to your repository
   - Look at URL: github.com/YOUR_USERNAME/YOUR_REPO
   - Copy: `YOUR_USERNAME/YOUR_REPO`

### Example

```
GitHub URL: https://github.com/avidcoder08/better-pesu-materials
Token: ghp_1234567890abcdefghijklmnopqrstuvwxyz
Repo Name: avidcoder08/better-pesu-materials
Branch: main
```

---

## ⚙️ Configuration File

### Create `.env` File

In your project root, create a file named `.env`:

```env
# Firebase - Copy the entire JSON from downloaded file
FIREBASE_SERVICE_ACCOUNT_JSON={"type": "service_account", "project_id": "your-id", ...}

# GitHub
GITHUB_TOKEN=ghp_your_token_here
GITHUB_REPO=your_username/your_repo_name
GITHUB_BRANCH=main

# Firebase Storage (optional)
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
```

### ⚠️ Important Notes

- Never commit `.env` to GitHub
- Never share your tokens
- Rotate tokens every 90 days
- Keep Firebase JSON private

### .env vs secrets.toml

**For Local Development:** Use `.env` file

**For Streamlit Cloud:** Use `.streamlit/secrets.toml`

Format for `secrets.toml`:

```toml
firebase_service_account_json = '''
{
  "type": "service_account",
  ...
}
'''
GITHUB_TOKEN = "ghp_xxx"
GITHUB_REPO = "username/repo"
GITHUB_BRANCH = "main"
```

---

## 💻 Installation & Setup

### 1. System Requirements

- Python 3.8 or higher
- pip (comes with Python)
- Git (optional, for version control)

### 2. Clone Project

```bash
cd your_project_directory
git clone https://github.com/yourusername/better-pesu-acad.git
cd better-pesu-acad
```

### 3. Create Virtual Environment (Recommended)

```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

**If error:** Remove this line from requirements.txt:
```
-e ./pesuacademy-dev
```

Then install manually:
```bash
pip install streamlit toml st-theme lxml python-dotenv requests cryptography extra-streamlit-components firebase-admin
```

### 5. Create Configuration File

Create `.env` in project root with your credentials (see Configuration section above)

### 6. Run the App

```bash
streamlit run main.py
```

App opens at `http://localhost:8501`

---

## 🔐 Login

### First Time Login

1. Open app (http://localhost:8501)
2. Email: `your@gmail.com` (from Firebase friends list)
3. Password: Any password (not validated yet)
4. Click "Login"

### Add More Friends

```python
# Option 1: Use Firebase Console (easiest)
# Go to Firestore → friends → allowed_emails → Edit emails array

# Option 2: Use Python
from firebase_utils import add_friend_email
add_friend_email("friend@gmail.com")
```

---

## 📱 Using the App

### Dashboard

- **Greeting:** Changes based on time of day
- **Tasks:** Create, view, and mark tasks complete
- **Sidebar:** Shows your email, logout button

### Course Materials

- **Upload:** Add materials by course code
- **Browse:** All materials organized by subject
- **Download:** Click "View File" to download
- **Delete:** Remove your own uploads

---

## 🐛 Troubleshooting

### Problem: "Firebase credentials not found"

**Solution:**
- Check `.env` file exists
- Verify Firebase JSON is valid (try validation.com)
- Check JSON is in correct format

### Problem: "Email not in friends list"

**Solution:**
- Email must be exact (case-sensitive)
- Add to Firebase: Firestore → friends → allowed_emails
- Wait a few seconds for sync

### Problem: "ModuleNotFoundError"

**Solution:**
```bash
pip install firebase-admin
# OR reinstall everything
pip install -r requirements.txt --force-reinstall
```

### Problem: "Permission denied on Firestore"

**Solution:**
- Update Firestore Rules (see Firebase Setup section)
- Or use simpler rules:
```javascript
match /{document=**} {
  allow read, write: if true;
}
```

### Problem: "Material upload fails"

**Solution:**
- Verify GitHub token is valid
- Check `GITHUB_REPO` format: `username/repo`
- Verify GitHub token has `repo` scope

### Problem: "Time greeting is wrong"

**Solution:**
```bash
# Set timezone
export TZ="Asia/Kolkata"
# Then run app
streamlit run main.py
```

---

## 🚀 Deployment

### Option 1: Streamlit Cloud (Recommended)

1. Push code to GitHub
2. Go to streamlit.io/cloud
3. Click "New app"
4. Select repository and `main.py`
5. Add secrets in Settings:
   - `FIREBASE_SERVICE_ACCOUNT_JSON`
   - `GITHUB_TOKEN`
   - `GITHUB_REPO`
   - `GITHUB_BRANCH`

### Option 2: Other Platforms (Heroku, AWS, etc.)

1. Create `.streamlit/secrets.toml` (not .env)
2. Add same configuration
3. Deploy normally
4. Set environment variables as needed

### Domain Setup

- Register domain (Namecheap, GoDaddy, etc.)
- Point to Streamlit Cloud or your server
- Configure SSL (automatic on Streamlit Cloud)

---

## 📊 Project Structure

```
better-pesu-acad/
├── main.py                    # Main app entry
├── pages/
│   ├── login.py              # Login page
│   ├── dashboard.py          # Tasks & greeting
│   └── courses.py            # Material sharing
├── firebase_utils.py         # Firebase helpers
├── github_utils.py           # GitHub integration
├── materials_utils.py        # Database helpers
├── session_utils.py          # Session management
├── requirements.txt          # Python packages
├── .env                      # Configuration (DON'T COMMIT)
├── README.md                 # Overview
├── SETUP_INSTRUCTIONS.md     # Detailed guide
├── CONFIGURATION.md          # Config examples
├── LAUNCH_CHECKLIST.md       # Deploy checklist
└── QUICKSTART.md            # Quick setup
```

---

## 🔒 Security Best Practices

### DO ✅

- Use `.env` for local, `secrets.toml` for Streamlit Cloud
- Add `.env` to `.gitignore`
- Rotate tokens regularly
- Use HTTPS in production
- Keep credentials private
- Review Firestore rules

### DON'T ❌

- Commit .env to GitHub
- Share Firebase JSON or tokens
- Use production database for testing
- Set Firestore rules to "allow all"
- Hardcode credentials
- Log sensitive data

---

## 📞 Getting Help

1. **Read the docs** - SETUP_INSTRUCTIONS.md, CONFIGURATION.md
2. **Check Troubleshooting** - Above or in docs
3. **Test configuration** - Run `test_config.py`
4. **Review logs** - Check browser console (F12) and terminal
5. **Check Firebase** - Verify settings in console
6. **Check GitHub** - Verify token and repository

---

## ✅ Pre-Launch Checklist

Before going live, verify:

- [ ] Firebase project created and configured
- [ ] Firestore database initialized
- [ ] Friends collection with emails created
- [ ] GitHub repository created
- [ ] Personal access token generated
- [ ] `.env` file configured with credentials
- [ ] App runs locally without errors
- [ ] Login works with test email
- [ ] Can upload materials
- [ ] Can download materials
- [ ] Tasks work
- [ ] `.env` added to `.gitignore`
- [ ] No credentials in any committed files
- [ ] app tested in multiple browsers

---

## 🎯 Next Steps

1. **Immediate:**
   - Set up Firebase (15 min)
   - Set up GitHub (10 min)
   - Configure app (5 min)
   - Run locally (2 min)
   - Total: ~30 min

2. **Soon:**
   - Add all friends to Firestore
   - Test with real users
   - Upload some materials
   - Gather feedback

3. **Later:**
   - Deploy to Streamlit Cloud
   - Set up custom domain
   - Plan new features
   - Monitor usage

---

## 📈 Features Overview

### Current Features ✅

- Firebase authentication (friends only)
- Task management & to-do list
- Course material uploading
- GitHub integration
- Time-based greeting
- Responsive design

### Planned Features 📋

- Password authentication
- User profiles
- Search functionality
- Material ratings
- Download history
- Sharing/collaboration
- Dark theme

---

## 💡 Tips & Tricks

### For Better Performance

- Keep Firestore documents small
- Index frequently searched fields
- Cache materials in browser
- Optimize images before uploading

### For Better UX

- Add course descriptions
- Organize materials by semester
- Include file size info
- Add upload timestamps

### For Security

- Review Firestore rules weekly
- Audit who has access
- Rotate tokens regularly
- Monitor API usage

---

## 📝 FAQ

**Q: Can I use this without Firebase?**
A: Not currently. Would require rewriting authentication.

**Q: Can I use without GitHub?**
A: Could use Firebase Storage instead, requires code changes.

**Q: Is password required?**
A: Currently no. Use only for trusted users or add Firebase Auth.

**Q: Can multiple people upload to same course?**
A: Yes! Anyone can upload materials by course code.

**Q: How much does this cost?**
A: Firebase free tier covers most use cases. GitHub is free.

**Q: Can I download all materials at once?**
A: Currently individual downloads. Could add batch download later.

---

## 📄 License & Credits

- Built with Streamlit
- Powered by Firebase
- Uses GitHub for storage
- Open source & community-driven

---

## 🎓 Made for PESU Community

This app was built to make course material sharing easier. Enjoy! 🚀

---

**Questions?** Check the detailed documentation files or reach out!

**Ready to launch?** Use LAUNCH_CHECKLIST.md before deploying!

**Version 1.0 - February 2026**
