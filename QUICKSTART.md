# ⚡ Quick Start Guide (5 Minutes)

Get Better PESU Acad running in under 5 minutes!

## Step 1: Firebase Setup (2 min)

1. Go to [firebase.google.com](https://firebase.google.com) → Create Project
2. Name it, create it
3. Go to **Firestore** → Create Database (Production mode)
4. Create collection `friends` with document `allowed_emails`
5. Add field `emails` (array) with your email: `["your@gmail.com"]`

## Step 2: Get Firebase Credentials (1 min)

1. Go to **Project Settings** ⚙️
2. **Service Accounts** tab → **Generate New Private Key**
3. JSON file downloads → **Keep it!**

## Step 3: Configure App (1 min)

Create `.env` file in project root:

```env
FIREBASE_SERVICE_ACCOUNT_JSON={"type": "service_account", "project_id": "...", ... }
GITHUB_TOKEN=ghp_xxx
GITHUB_REPO=username/repo
GITHUB_BRANCH=main
```

**Paste your entire Firebase JSON** (copy everything from downloaded file)

## Step 4: Install & Run (1 min)

```bash
pip install -r requirements.txt
streamlit run main.py
```

Done! 🎉 App opens at `http://localhost:8501`

---

## Login

- **Email:** Your email (from friends list)
- **Password:** Any password (not validated yet)

---

## Next Steps

- Read **SETUP_INSTRUCTIONS.md** for detailed info
- Read **CONFIGURATION.md** for config examples
- Add more friends to Firestore

**Questions?** Check the full documentation!
