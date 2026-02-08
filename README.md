# Better PESU Acad 📚

A secure, lightweight educational platform for sharing course materials and managing tasks. Built with Streamlit, Firebase, and GitHub.

![Status](https://img.shields.io/badge/status-active-success)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ Features

- 🔐 **Firebase Authentication** - Only invited friends can access
- 📚 **Course Materials** - Upload and share materials by subject
- 🌐 **GitHub Storage** - Materials stored securely in GitHub
- ✅ **Task Management** - Dashboard with to-do list
- ⏰ **Smart Greetings** - Time-based greetings (morning/afternoon/evening)
- 📱 **Responsive UI** - Works on desktop and mobile

---

## 🚀 Quick Start

**Want to get running in 5 minutes?**

👉 See **[QUICKSTART.md](QUICKSTART.md)**

---

## 📖 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** ⚡ - 5-minute setup guide
- **[SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)** 📋 - Detailed step-by-step guide
- **[CONFIGURATION.md](CONFIGURATION.md)** ⚙️ - Configuration examples and troubleshooting

---

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Git
- Firebase account (free)
- GitHub account

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/better-pesu-acad.git
   cd better-pesu-acad
   ```

2. **Create virtual environment** (optional)
   ```bash
   python -m venv venv
   # On Windows: .\venv\Scripts\Activate.ps1
   # On Mac/Linux: source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure credentials** (see [CONFIGURATION.md](CONFIGURATION.md))
   - Create `.env` file with Firebase & GitHub credentials

5. **Run the app**
   ```bash
   streamlit run main.py
   ```

App will open at `http://localhost:8501` 🎉

---

## 📦 What's Included

```
better-pesu-acad/
├── main.py                 # Entry point (authentication)
├── pages/
│   ├── login.py           # Login with Firebase
│   ├── dashboard.py       # Task management
│   └── courses.py         # Material sharing
├── firebase_utils.py      # Firebase helpers
├── github_utils.py        # GitHub integration
├── materials_utils.py     # Data management
├── session_utils.py       # Session handling
├── requirements.txt       # Dependencies
└── README.md             # This file
```

---

## 🔐 Authentication

- Users must be in the **friends list** on Firebase
- For now, password is not validated
- In production, consider using proper Firebase Authentication

### Add Authorized Users

**Option 1: Firebase Console**
1. Go to Firestore
2. Edit `friends` → `allowed_emails` array
3. Add email addresses

**Option 2: Python Script**
```python
from firebase_utils import add_friend_email
add_friend_email("friend@gmail.com")
```

---

## 📚 Usage

### Dashboard
- View time-based greeting
- Create and manage tasks
- Mark tasks as complete

### Course Materials
- **Upload:** Add course materials by subject
- **Browse:** View all uploaded materials
- **Share:** Materials accessible to all friends
- **Delete:** Remove your own uploads

### Sidebar
- Shows logged-in user email
- Logout button

---

## 🔧 Configuration

### Firebase
- Firestore database for friends list and data
- Service Account JSON for authentication

### GitHub
- Stores course materials
- Personal Access Token for access
- Repository for file storage

See **[CONFIGURATION.md](CONFIGURATION.md)** for detailed examples.

---

## 📋 System Requirements

| Component | Requirement |
|-----------|-------------|
| Python | 3.8 or higher |
| Streamlit | Latest version |
| Firebase | Free tier or paid |
| GitHub | Free account sufficient |
| Python Packages | See requirements.txt |

---

## 🐛 Troubleshooting

### Firebase credentials not found
→ See [CONFIGURATION.md - Firebase Setup](CONFIGURATION.md#how-to-get-your-firebase-service-account-json)

### Email not authorized
→ Check Firestore friends list, add email if missing

### Materials not uploading
→ Verify GitHub token and repository name

### Wrong timezone for greetings
→ Set `TZ` environment variable (e.g., `TZ=Asia/Kolkata`)

**More help?** Check [SETUP_INSTRUCTIONS.md - Troubleshooting](SETUP_INSTRUCTIONS.md#-troubleshooting)

---

## 🌐 Deployment

### Local Development
```bash
streamlit run main.py
```

### Streamlit Cloud
1. Push code to GitHub
2. [Streamlit Cloud](https://streamlit.io/cloud)
3. Create new app from repo
4. Add secrets in settings

### Other Platforms
Works with any Python hosting (Heroku, AWS, Azure, etc.)

---

## 📝 Architecture

```
User Login (Firebase)
    ↓
Session Created
    ↓
Navigation Menu (Dashboard / Courses)
    ↓
Dashboard
├── Tasks (Streamlit session state)
└── Time-based greeting
    ↓
Course Materials
├── Upload (GitHub)
└── Display (Firestore index)
```

---

## 🔒 Security Notes

- ⚠️ Passwords not validated (use Firebase Auth for production)
- ⚠️ Firestore rules set to allow all (tighten for production)
- ✅ GitHub token never exposed in frontend
- ✅ Firebase credentials only server-side

---

## 🤝 Contributing

Want to improve PESU Acad?

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/awesome-feature`)
3. Commit changes (`git commit -m 'Add awesome feature'`)
4. Push to branch (`git push origin feature/awesome-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 📞 Support

- 📖 Read the documentation
- 🐛 Check [Troubleshooting](SETUP_INSTRUCTIONS.md#-troubleshooting)
- 💬 Ask questions in Issues

---

## 🎯 Roadmap

- [ ] Email-based password authentication
- [ ] Material download history
- [ ] Search functionality
- [ ] Sharing / collaborative uploads
- [ ] Material ratings and comments
- [ ] User profiles
- [ ] Dark/light theme toggle

---

## 🙌 Acknowledgments

Built with:
- [Streamlit](https://streamlit.io/) - UI Framework
- [Firebase](https://firebase.google.com/) - Authentication & Database
- [GitHub](https://github.com/) - File Storage

---

## 📈 Stats

- 📦 ~1000 lines of code
- 🔐 Firebase + GitHub integrated
- 🚀 Ready to deploy
- 📚 Fully documented

---

**Made with ❤️ for the PESU Community**

Questions? Check the [docs](SETUP_INSTRUCTIONS.md) or open an issue! 🚀
