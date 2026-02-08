# Firebase Authentication Setup

This app now uses **Firebase Authentication** for secure email/password login.

## ✅ Setup Steps

### 1. Enable Firebase Authentication

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select your project
3. Go to **Authentication** (left sidebar)
4. Click **"Get Started"**
5. Click on **"Email/Password"** provider
6. Toggle **"Enable"** to ON
7. Click **"Save"**

### 2. Get Your Web API Key

1. Go to **Project Settings** (⚙️ icon, top right)
2. Click **"General"** tab
3. Scroll down to find **"Your apps" → "Web"**
4. Look for **apiKey** value
   - Or create a new web app: Click **"Add app" → "</>" (web)**
   - Copy the `apiKey` from the config

Example config you'll see:
```javascript
const firebaseConfig = {
  apiKey: "AIzaSyDxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",  // <- COPY THIS
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project",
  ...
};
```

### 3. Add to Configuration

Add to your `.env` file:

```env
FIREBASE_WEB_API_KEY=AIzaSyDxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Or add to `.streamlit/secrets.toml`:

```toml
FIREBASE_WEB_API_KEY = "AIzaSyDxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the App

```bash
streamlit run main.py
```

## 🎯 Usage

### Sign Up (Create New Account)

1. Click **"Sign Up"** tab
2. Enter email and password (min 6 chars)
3. Click **"Sign Up"**
4. Logged in automatically!

### Login (Existing Account)

1. Click **"Login"** tab
2. Enter your email and password
3. Click **"Login"**
4. Access the app!

### Password Reset

Forgot your password? No problem!

1. Click **"Forgot your password?"** on login page
2. Enter your email address
3. Check your email for reset link
4. Copy the code from the email
5. Enter code and set new password
6. Login with new password!

**Step by step:**
- Step 1: Request reset (email required)
- Step 2: Enter reset code from email
- Step 3: Set new password

### Logout

- Click **"Logout"** button in sidebar
- Session cleared

## 🔐 Security Features

✅ Passwords hashed by Firebase  
✅ Secure token-based authentication  
✅ Email verification (optional)  
✅ Account recovery  
✅ Password reset  

## 🚀 Advanced Features (Optional)

### Email Verification

Add to login page after sign up:

```python
# Send verification email
from firebase_auth import send_email_verification
send_email_verification(email)
```

### Password Reset

The app already has a built-in password reset feature!

**User Flow:**
1. Click "Forgot your password?" on login page
2. Enter email
3. Firebase sends reset email
4. User enters reset code
5. User sets new password

**Backend Functions:**
```python
from firebase_auth import send_password_reset, confirm_password_reset

# Step 1: Send reset email
result = send_password_reset("user@example.com")

# Step 2: Confirm new password with code from email
result = confirm_password_reset(reset_code, new_password)
```

**Password Reset Page:**
- Located at: `pages/password_reset.py`
- Link on login page: "Forgot your password?"
- 3-step process with validation
- User-friendly error messages

### Delete Account

```python
from firebase_auth import delete_account
delete_account(id_token)
```

## � Email Configuration

Push notifications and password reset emails are sent through Firebase. To customize the email:

### Password Reset Email Template

1. Go to **Authentication** → **Templates** tab
2. Click **"Password reset"**
3. Customize sender email and template
4. Click **"Save"**

**Default template sends link with reset code that user uses to set new password.**

---

### "FIREBASE_WEB_API_KEY not found"

**Solution:**
- Add to `.env`: `FIREBASE_WEB_API_KEY=your_key_here`
- Or `.streamlit/secrets.toml`: `FIREBASE_WEB_API_KEY = "your_key_here"`
- Restart Streamlit: `streamlit run main.py`

### "Invalid email" error

**Solution:**
- Check email format (must be valid email)
- Try simple email like: `test@example.com`

### "Weak password" error

**Solution:**
- Password must be minimum 6 characters
- Can include special characters for better security

### "Too many failed login attempts"

**Solution:**
- Wait a few minutes and try again
- Firebase blocks repeated failed attempts for security

### "Email already exists"

**Solution:**
- That email is already registered
- Use "Login" tab instead of "Sign Up"
- Or use different email

### "Reset code expired"

**Solution:**
- Password reset codes expire after 1 hour
- Click **"Start Over"** to request a new reset email
- Check spam folder for reset email

### "Didn't receive reset email"

**Solution:**
- Check spam/junk folder
- Verify email address is correct
- Check if email is registered (try login first)
- Wait a few minutes and try again
- Firebase may rate-limit requests

## 📊 Manage Users

### In Firebase Console

1. Go to **Authentication**
2. Click **"Users"** tab
3. See all registered users
4. Click user to view details
5. Can delete or disable users

### Via Python Script

```python
from firebase_admin import auth

# Create user (server-side)
user = auth.create_user(
    email='user@example.com',
    password='securePassword123'
)

# Disable user
auth.disable_user(user.uid)

# Delete user
auth.delete_user(user.uid)
```

## 🔄 Session Management

Sessions are stored in Streamlit's session state:

```python
st.session_state.authenticated  # True/False
st.session_state.user_email     # "user@example.com"
st.session_state.user_id        # Firebase UID
st.session_state.id_token       # Firebase token
```

Sessions persist while app is open.

## 📱 Deploying to Streamlit Cloud

1. Push code to GitHub
2. Deploy via Streamlit Cloud
3. Add to **"Advanced settings → Secrets"**:

```toml
FIREBASE_WEB_API_KEY = "your_key_here"
```

4. Deploy!

## 🆚 Comparison: Old vs New

| Feature | Old | New |
|---------|-----|-----|
| Authentication | Friends list only | Proper Firebase Auth |
| Sign Up | Not available | ✅ Available |
| Password | Not validated | ✅ Secured & hashed |
| User Management | Manual list | ✅ Firebase dashboard |
| Scale | ~10 users | Unlimited users |
| Account Recovery | None | ✅ Available |

## ✨ Next Steps

1. ✅ Enable Firebase Authentication
2. ✅ Get Web API Key
3. ✅ Add to `.env` or `secrets.toml`
4. ✅ Install dependencies
5. ✅ Run the app
6. ✅ Create your account!

---

## 📞 Need Help?

- Check [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)
- Check [CONFIGURATION.md](CONFIGURATION.md)
- Review [COMPLETE_REFERENCE.md](COMPLETE_REFERENCE.md)
- Check Firebase Console → Authentication → Logs

---

**Version 2.0 - Firebase Authentication Enabled** 🔐
