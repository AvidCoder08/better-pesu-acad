# Pre-Launch Checklist

Use this checklist before deploying Better PESU Acad to production.

---

## ✅ Firebase Setup

- [ ] Firebase project created
- [ ] Firestore database initialized
- [ ] `friends` collection created
- [ ] `allowed_emails` document created with email array
- [ ] Service account JSON downloaded and secured
- [ ] Firebase rules reviewed (customize for production)

**Firestore Rules (Production Safe):**
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Only authenticated users can access
    match /friends/allowed_emails {
      allow read: if true;
      allow write: if false; // Modify via Python only
    }
    match /materials/{document=**} {
      allow read: if true;
      allow write: if false; // Modify via Python only
    }
  }
}
```

---

## ✅ GitHub Setup

- [ ] GitHub repository created (public or private)
- [ ] Personal Access Token generated
- [ ] Token has `repo` scope enabled
- [ ] Repository has `main` branch (or configured branch)
- [ ] GitHub credentials stored safely

**GitHub Token Scopes (Minimum):**
- ✅ `repo` (Full control of repositories)
- ✅ `read:user` (Read user profile)

---

## ✅ Code Security

- [ ] No hardcoded credentials in code
- [ ] `.env` file added to `.gitignore`
- [ ] `.streamlit/secrets.toml` NOT committed to GitHub
- [ ] All dependencies in `requirements.txt` pinned to versions
- [ ] No test/debug code left behind

**Update .gitignore:**
```
.env
.streamlit/secrets.toml
venv/
__pycache__/
*.pyc
.DS_Store
```

---

## ✅ Configuration

- [ ] Firebase service account JSON correctly formatted
- [ ] All environment variables set:
  - `FIREBASE_SERVICE_ACCOUNT_JSON`
  - `FIREBASE_STORAGE_BUCKET`
  - `GITHUB_TOKEN`
  - `GITHUB_REPO`
  - `GITHUB_BRANCH`
- [ ] `.env` or `secrets.toml` matches deployment platform
- [ ] Configuration tested locally

---

## ✅ Friends List

- [ ] All authorized users added to friends list
- [ ] Emails spelled correctly (case-sensitive)
- [ ] Test login with at least one user

**Check Firestore:**
```
Collection: friends
Document: allowed_emails
Field: emails (array)
Values: ["user1@gmail.com", "user2@gmail.com", ...]
```

---

## ✅ Testing

- [ ] Local testing completed
- [ ] Login works with test email
- [ ] Dashboard loads without errors
- [ ] Can upload a test file
- [ ] Can view uploaded materials
- [ ] Tasks creation works
- [ ] Logout works
- [ ] App handles errors gracefully

**Test Scenarios:**
- [ ] Login with valid email
- [ ] Login with invalid email (should deny)
- [ ] Upload single file
- [ ] Upload multiple files
- [ ] Download/view uploaded file
- [ ] Delete uploaded file
- [ ] Create task
- [ ] Complete task
- [ ] Do task operations under load

---

## ✅ Performance

- [ ] Page load time < 3 seconds
- [ ] Firestore queries optimized
- [ ] No console errors (check browser F12)
- [ ] No Python errors in terminal
- [ ] Memory usage reasonable

---

## ✅ Documentation

- [ ] README.md complete and accurate
- [ ] SETUP_INSTRUCTIONS.md reviewed
- [ ] CONFIGURATION.md examples correct
- [ ] QUICKSTART.md tested
- [ ] Code comments added where needed

---

## ✅ Streamlit Cloud Deployment

If deploying to Streamlit Cloud:

- [ ] Code pushed to GitHub
- [ ] GitHub repository linked to Streamlit
- [ ] `main.py` is entry point
- [ ] Secrets configured in Streamlit settings:
  ```
  FIREBASE_SERVICE_ACCOUNT_JSON
  GITHUB_TOKEN
  GITHUB_REPO
  GITHUB_BRANCH
  FIREBASE_STORAGE_BUCKET
  ```
- [ ] App deployed successfully
- [ ] Tested on deployed version

**Deploy:**
1. Connect GitHub repo to [Streamlit Cloud](https://streamlit.io/cloud)
2. Select `main.py` as entry point
3. Add secrets via "Advanced settings"
4. Deploy!

---

## ✅ Custom Domain (Optional)

If using custom domain:

- [ ] Domain registered (e.g., betterpesU.com)
- [ ] DNS records configured
- [ ] SSL certificate obtained (auto for Streamlit Cloud)
- [ ] Domain points to app

---

## ✅ Monitoring

- [ ] Set up error tracking (optional: Sentry, etc.)
- [ ] Monitor Firestore usage
- [ ] Monitor GitHub API rate limits
- [ ] Check logs regularly

---

## ✅ Backup & Recovery

- [ ] Firestore data backup plan
- [ ] GitHub repo backed up
- [ ] Environment secrets backed up securely
- [ ] Recovery procedure documented

---

## ⚠️ Security Review

**Authentication:**
- [ ] Only friends can login
- [ ] Session handling secure
- [ ] No sensitive data in localStorage

**Data:**
- [ ] No passwords stored
- [ ] No personal data exposed
- [ ] Materials accessible only to authenticated users

**Tokens:**
- [ ] GitHub token never logged
- [ ] Firebase credentials server-side only
- [ ] No secrets in browser console

---

## 📱 Browser Compatibility

Test on:
- [ ] Chrome (desktop)
- [ ] Firefox (desktop)
- [ ] Safari (desktop)
- [ ] Chrome (mobile)
- [ ] Safari (mobile)

---

## 📋 Post-Launch

After deployment:

- [ ] Monitor error logs daily
- [ ] Gather user feedback
- [ ] Track usage metrics
- [ ] Plan next features
- [ ] Update documentation if needed
- [ ] Rotate GitHub token every 90 days

---

## 🎯 Go Live Criteria

All items above must be ✅ before going live:

- ✅ Firebase configured
- ✅ GitHub configured
- ✅ Code secure (no hardcoded secrets)
- ✅ All tests passing
- ✅ Documentation complete
- ✅ Friends list populated
- ✅ Deployed and working

---

## 📝 Final Checklist

Before clicking "Deploy":

- [ ] Did I commit code to GitHub?
- [ ] Are secrets NOT in the repo?
- [ ] Did I test login locally?
- [ ] Did I test uploading materials?
- [ ] Did I add all friends to Firestore?
- [ ] Did I verify GitHub token works?
- [ ] Did I review the URL I'm deploying to?
- [ ] Did I have someone else test it?

---

**Ready to Go Live? 🚀**

Once all items are checked, you're good to deploy!

Questions? Check [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) or [CONFIGURATION.md](CONFIGURATION.md).
