# Streamlit Secrets Configuration Guide

Your app now uses **Streamlit's secrets.toml** for managing sensitive credentials. This is more secure and convenient than using .env files!

## Benefits of Using secrets.toml

✅ **Secure** - Never accidentally commit secrets to git  
✅ **Native** - Built into Streamlit, no extra tools needed  
✅ **Cloud-Ready** - Easy to deploy to Streamlit Cloud with environment secrets  
✅ **Convenient** - Access secrets directly with `st.secrets`  

## Local Setup

### 1. File Location

Your secrets are stored in:
```
.streamlit/secrets.toml
```

This file is already in your `.gitignore`, so it won't be committed to git.

### 2. Configuration Format

Secrets are written in TOML format (simple key = value pairs):

```toml
# Firebase Configuration
firebase_service_account = "firebase-credentials.json"

# GitHub Configuration
github_token = "github_pat_..."
github_repo = "username/repo"
github_branch = "main"

# Google Drive Configuration (optional)
google_drive_shared_drive_id = "your-id"
google_drive_service_account_json = """{"type":"service_account",...}"""
```

### 3. Available Secrets

| Secret | Purpose | Type |
|--------|---------|------|
| `firebase_service_account` | Path to Firebase credentials file | String (file path) |
| `github_token` | GitHub Personal Access Token | String |
| `github_repo` | GitHub repository (username/repo) | String |
| `github_branch` | Git branch for storage | String |
| `google_drive_service_account` | Path to Google Drive credentials (optional) | String (file path) |
| `google_drive_service_account_json` | Google Drive credentials as JSON (optional) | String (JSON) |
| `google_drive_shared_drive_id` | Google Drive Shared Drive ID (optional) | String |

## Local Development

When you run `streamlit run main.py`:
- Streamlit automatically loads secrets from `.streamlit/secrets.toml`
- Your app accesses them via `st.secrets.get("key_name")`
- If a secret isn't found in secrets.toml, it falls back to environment variables

## Deploying to Streamlit Cloud

When you deploy to [Streamlit Cloud](https://streamlit.io/cloud):

1. Go to your app's **Advanced settings**
2. Scroll to **Secrets**
3. Paste your secrets (don't include the file)

Example for Streamlit Cloud secrets:
```
firebase_service_account = firebase-credentials.json
github_token = github_pat_...
github_repo = username/repo
github_branch = main
```

## Accessing Secrets in Code

Secrets are already integrated into your utility files:

```python
# Firebase utils - automatically uses st.secrets
from firebase_utils import get_firestore_client
db = get_firestore_client()

# GitHub utils - automatically uses st.secrets
from github_utils import upload_to_github
url = upload_to_github(file_bytes, "path/to/file")
```

You don't need to manually access `st.secrets` - it's handled internally!

## Troubleshooting

### Secret Not Found Error
- Check `.streamlit/secrets.toml` exists
- Verify the key name matches exactly (case-sensitive)
- Restart Streamlit after editing secrets.toml

### "secrets.toml" is empty
- Create the file: `.streamlit/secrets.toml`
- Copy values from your `.env` file
- Reference the template: `.streamlit/secrets.example.toml`

### Still using .env? That's OK!
The utilities support both:
1. **Streamlit secrets.toml** (preferred)
2. **.env file** (fallback)

Just keep your `.env` file for local development if you prefer!

## Security Best Practices

🔒 **Never commit secrets.toml** - It's in .gitignore  
🔒 **Use file paths when possible** - Easier to manage and rotate  
🔒 **Rotate tokens regularly** - GitHub tokens, etc.  
🔒 **Use Streamlit Cloud secrets for deployment** - Don't paste secrets in code  
🔒 **Keep firebase-credentials.json safe** - Store it securely, don't share  

## Migration Checklist

✅ Copy secrets from `.env` to `.streamlit/secrets.toml`  
✅ Verify `.streamlit/secrets.toml` is in `.gitignore`  
✅ Restart Streamlit (`streamlit run main.py`)  
✅ Test upload/download functionality  
✅ Confirm calendar events load  
✅ Remove or comment out the `.env` file once you verify everything works  

## Example secrets.toml

```toml
# Firebase Configuration
firebase_service_account = "firebase-credentials.json"

# GitHub Configuration
github_token = "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"
github_repo = "AvidCoder08/pesu-teacher-materials"
github_branch = "main"

# Google Drive Configuration (optional)
google_drive_shared_drive_id = "19GN5iNYIUoULJbmC1XO8hNbAUulJGRv2"
google_drive_service_account_json = """{"type":"service_account",...full JSON...}"""
```

That's it! Your app is now using Streamlit's secure secrets management system! 🎉
