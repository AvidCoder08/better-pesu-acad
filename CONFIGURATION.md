# Configuration Examples

## Option 1: Using `.env` File (Local Development)

Create a file named `.env` in the root directory:

```env
# ===== FIREBASE CONFIGURATION =====
# Paste your entire Firebase Service Account JSON here (all on one line, escaped quotes)
FIREBASE_SERVICE_ACCOUNT_JSON={"type": "service_account", "project_id": "your-project-id", "private_key_id": "abc123...", "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBA...\n-----END PRIVATE KEY-----\n", "client_email": "firebase-adminsdk-xxxxx@your-project-id.iam.gserviceaccount.com", "client_id": "123456789", "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token", "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs", "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40your-project-id.iam.gserviceaccount.com"}

# Firebase Storage Bucket (from Firebase Console)
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com

# ===== GITHUB CONFIGURATION =====
# GitHub Personal Access Token (create at https://github.com/settings/tokens)
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Your GitHub repository name (format: username/repo-name)
GITHUB_REPO=your_username/your_repo_name

# Git branch where materials will be stored
GITHUB_BRANCH=main
```

## Option 2: Using `.streamlit/secrets.toml` (Streamlit Cloud)

Create a file at `.streamlit/secrets.toml`:

```toml
# ===== FIREBASE CONFIGURATION =====
# Your Firebase Service Account as a raw JSON string
firebase_service_account_json = '''
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBA...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-xxxxx@your-project-id.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40your-project-id.iam.gserviceaccount.com"
}
'''

# Firebase Storage Bucket
firebase_storage_bucket = "your-project-id.appspot.com"

# ===== GITHUB CONFIGURATION =====
# GitHub Token
GITHUB_TOKEN = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# GitHub Repository
GITHUB_REPO = "your_username/your_repo_name"

# GitHub Branch
GITHUB_BRANCH = "main"
```

---

## How to Get Your Firebase Service Account JSON

1. Open [Firebase Console](https://console.firebase.google.com)
2. Select your project
3. Click **⚙️ Settings** (top right)
4. Go to **"Service Accounts"** tab
5. Click **"Generate New Private Key"**
6. A JSON file will download automatically
7. Open it and copy the entire contents
8. Paste into `.env` or `.streamlit/secrets.toml`

**Example Firebase JSON:**
```json
{
  "type": "service_account",
  "project_id": "better-pesu-acad-12345",
  "private_key_id": "a1b2c3d4e5f6...",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQE...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-abcde@better-pesu-acad-12345.iam.gserviceaccount.com",
  "client_id": "123456789012345678901",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-abcde%40better-pesu-acad-12345.iam.gserviceaccount.com"
}
```

---

## How to Get GitHub Token

1. Go to [GitHub Settings → Developer settings](https://github.com/settings/apps)
2. Click on **"Personal access tokens"** → **"Tokens (classic)"**
3. Click **"Generate new token"**
4. Name it: `better-pesu-acad`
5. Set expiration: 90 days (or longer)
6. Select scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `read:user`
7. Click **"Generate token"**
8. **Copy immediately** (you won't see it again!)
9. Paste into `.env` or `.streamlit/secrets.toml`

**Example Token:**
```
ghp_1234567890abcdefghijklmnopqrstuvwxyz
```

---

## How to Get GitHub Repo Name

1. Go to your GitHub repository
2. Look at the URL: `https://github.com/YOUR_USERNAME/YOUR_REPO_NAME`
3. Copy `YOUR_USERNAME/YOUR_REPO_NAME`
4. This goes in `GITHUB_REPO` variable

**Example:**
```
avidcoder08/better-pesu-acad
```

---

## Firebase Storage Bucket Name

1. Open [Firebase Console](https://console.firebase.google.com)
2. Select your project
3. Go to **"Storage"** section
4. Your bucket name appears in the format: `your-project-id.appspot.com`
5. Copy and paste it

---

## Verification Checklist

After setting up configuration:

- [ ] `.env` file exists in project root OR `.streamlit/secrets.toml` exists
- [ ] Firebase JSON is properly formatted (valid JSON)
- [ ] Firebase project has Firestore database created
- [ ] `friends` collection exists with `allowed_emails` document
- [ ] GitHub token is valid and has `repo` scope
- [ ] GitHub repository exists and is accessible
- [ ] All environment variables have correct values (no typos)

---

## Common Configuration Mistakes

### ❌ Mistake 1: Invalid JSON Format
```
# WRONG - extra escaping
FIREBASE_SERVICE_ACCOUNT_JSON=\"{\\"type\\": \\"service_account\\"...}\"

# RIGHT - direct JSON
FIREBASE_SERVICE_ACCOUNT_JSON={"type": "service_account"...}
```

### ❌ Mistake 2: Missing Environment Variables
```
# WRONG - incomplete GitHub config
GITHUB_TOKEN=ghp_xxx

# RIGHT - all config present
GITHUB_TOKEN=ghp_xxx
GITHUB_REPO=username/repo
GITHUB_BRANCH=main
```

### ❌ Mistake 3: Wrong Repo Format
```
# WRONG
GITHUB_REPO=https://github.com/username/repo
GITHUB_REPO=username

# RIGHT
GITHUB_REPO=username/repo
```

### ❌ Mistake 4: Quotes in TOML
```
# WRONG in .streamlit/secrets.toml
firebase_service_account_json = {type: "service_account"...}

# RIGHT - use triple quotes for multiline
firebase_service_account_json = '''
{
  "type": "service_account"...
}
'''
```

---

## Testing Your Configuration

After setting up, run this Python script to verify:

```python
import os
from dotenv import load_dotenv
from firebase_utils import get_firestore_client

# Load .env
load_dotenv()

# Test Firebase
try:
    db = get_firestore_client()
    print("✅ Firebase connected!")
    
    # Check friends collection
    friends = db.collection("friends").document("allowed_emails").get()
    if friends.exists:
        emails = friends.get("emails", [])
        print(f"✅ Found {len(emails)} authorized friends")
        print(f"   Emails: {emails}")
    else:
        print("⚠️  No friends collection found")
except Exception as e:
    print(f"❌ Firebase Error: {e}")

# Test GitHub
try:
    from github_utils import _get_github_config
    config = _get_github_config()
    print("✅ GitHub configured!")
    print(f"   Repo: {config['repo']}")
    print(f"   Branch: {config['branch']}")
except Exception as e:
    print(f"❌ GitHub Error: {e}")

print("\n✅ Configuration test complete!")
```

Save as `test_config.py` and run:
```bash
python test_config.py
```

---

## Help!

If you're stuck:

1. Re-read the relevant section above
2. Check for typos in configuration
3. Verify Firebase/GitHub settings online
4. Run `test_config.py` to identify issues
5. Check `.env` or `secrets.toml` file permissions
