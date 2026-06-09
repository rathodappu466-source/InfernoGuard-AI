# 🚀 InfernoGuard AI — Quick Start Guide

## 📋 Prerequisites

- **Python 3.14+** (you have 3.14.5 ✅)
- **pip** package manager
- **Webcam** (optional, for live detection)
- **YOLOv8 model** (already included at `models/best.pt` ✅)

---

## ⚡ Quick Start (30 seconds)

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Run the Application
```powershell
streamlit run app.py
```

### 3. Open Browser
Navigate to: **http://localhost:8501**

### 4. Create Account
- Click "Create Account" tab
- Enter username, email, password
- Click "Sign Up"

### 5. Start Detecting! 🔥
- Go to "Live Detection" page
- Select "Webcam" as video source
- Click "Start Detection"

---

## 🧹 One-Time Cleanup (Recommended)

### Delete Unnecessary Files:
```powershell
# 1. Delete virtual environment folder (if it exists)
Remove-Item "infernoguard_ai" -Recurse -Force -ErrorAction SilentlyContinue

# 2. Clean Python cache
Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
```

---

## 🔧 Configuration

### Email Alerts:
1. Go to **Settings** → **Integrations** tab
2. Configure SMTP settings (Gmail example):
   - SMTP Host: `smtp.gmail.com`
   - SMTP Port: `587`
   - Sender Email: `your-email@gmail.com`
   - Password: `your-app-password` (use App Password, not regular password)
   - Recipient Email: `recipient@example.com`
3. Enable Email Alerts in **Settings** → **Alerts** tab

### Telegram Alerts:
1. Create a Telegram bot via [@BotFather](https://t.me/botfather)
2. Get your Chat ID from [@userinfobot](https://t.me/userinfobot)
3. Go to **Settings** → **Integrations** tab
4. Enter Bot Token and Chat ID
5. Enable Telegram Alerts in **Settings** → **Alerts** tab

### RTSP Camera:
1. Go to **Settings** → **Integrations** tab
2. Enter RTSP URL (format: `rtsp://user:pass@ip:port/stream`)
3. Go to **Live Detection**
4. Select "RTSP Stream" as video source

---

## 📊 Features Overview

### 🏠 Dashboard
- Real-time system status
- Incident statistics
- AI performance metrics
- Recent incidents feed
- Safety recommendations

### 🎥 Live Detection
- Webcam detection
- RTSP camera streams
- Video file upload
- Real-time FPS display
- Emergency alerts

### 📈 Analytics
- Safety score gauge
- Risk heatmaps
- Detection trends
- Confidence analysis
- AI-powered insights

### 📜 Incident History
- Full incident audit trail
- Filter by type (fire/smoke)
- Search functionality
- CSV/JSON export
- AI analysis per incident

### ⚙️ Settings
- Profile management
- Alert configuration
- Integration setup (Email, Telegram, RTSP)
- Security settings

---

## 🧪 Testing

### Run Tests:
```powershell
# Install test dependencies
pip install pytest hypothesis

# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_auth.py -v
```

---

## ⚠️ Troubleshooting

### Issue: Port Already in Use
```powershell
# Run on different port
streamlit run app.py --server.port 8502
```

### Issue: Model Not Found
```
Error: Model file not found
```
**Solution:** Ensure `models/best.pt` exists

### Issue: Log File Locked
```
PermissionError: infernoguard.log
```
**Solution:**
```powershell
# Stop all Python processes
Get-Process python | Stop-Process -Force

# Delete log files
Remove-Item "*.log" -Force

# Restart application
streamlit run app.py
```

### Issue: Webcam Not Working
**Solution:**
- Check if another application is using the webcam
- Try "Upload Video" or "RTSP Stream" instead

### Issue: Database Error
```powershell
# Reset database (WARNING: deletes all data)
Remove-Item "database\infernoguard.db" -Force
streamlit run app.py  # Auto-recreates tables
```

---

## 🔐 Security Notes

- ✅ Passwords are bcrypt-hashed (industry standard)
- ✅ Sessions are secure
- ✅ SQL injection protection via parameterized queries
- ⚠️ **IMPORTANT:** Never commit `.env` files or passwords to version control

---

## 📁 Project Structure

```
Project Root/
├── app.py                  # Main entry point
├── requirements.txt        # Dependencies
├── .gitignore              # Git ignore rules
│
├── pages/                  # Streamlit pages
│   ├── 1_Dashboard.py
│   ├── 2_Live_Detection.py
│   ├── 3_Analytics.py
│   ├── 4_Incident_History.py
│   └── 5_Settings.py
│
├── detection/              # Detection engines
│   ├── detector.py         # YOLOv8 wrapper
│   ├── webcam.py           # Webcam stream
│   ├── rtsp.py             # RTSP stream
│   └── video_detection.py  # Video file stream
│
├── alerts/                 # Alert systems
│   ├── sound_alert.py
│   ├── email_alert.py
│   ├── telegram_alert.py
│   └── cooldown.py
│
├── auth/                   # Authentication
│   ├── login.py
│   ├── signup.py
│   └── session.py
│
├── database/               # Database layer
│   ├── db.py               # CRUD operations
│   └── schema.py           # Table definitions
│
├── analytics/              # Analytics & charts
│   ├── charts.py
│   └── dashboard.py
│
├── history/                # History filtering
│   └── logs.py
│
├── utils/                  # Utilities
│   ├── config.py           # Configuration
│   ├── helpers.py          # Helper functions
│   ├── logger.py           # Logging
│   └── ui.py               # UI components
│
├── models/                 # AI models
│   └── best.pt             # YOLOv8 model
│
├── assets/                 # Static files
│   └── styles.css          # Custom CSS
│
├── tests/                  # Test suite
│   ├── test_auth.py
│   ├── test_detector.py
│   ├── test_alerts.py
│   ├── test_database.py
│   ├── test_helpers.py
│   └── test_history.py
│
└── screenshots/            # Detection screenshots
```

---

## 📝 Common Commands

```powershell
# Start app
streamlit run app.py

# Start with auto-reload
streamlit run app.py --server.runOnSave true

# Start on specific port
streamlit run app.py --server.port 8502

# Run tests
pytest tests/ -v

# Clean cache
Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force

# Clean logs
Remove-Item "*.log" -Force

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## 🎯 Next Steps

1. ✅ **Run the application** — Follow Quick Start above
2. ✅ **Create an account** — Sign up with username/email/password
3. ✅ **Test webcam detection** — Try the Live Detection page
4. ✅ **Configure alerts** — Set up email/Telegram in Settings
5. ✅ **Explore analytics** — Check out the Analytics page
6. ✅ **Review documentation** — Read PROJECT_HEALTH_REPORT.md

---

## 🆘 Need Help?

1. Check **PROJECT_HEALTH_REPORT.md** for comprehensive information
2. Read **TESTING_CHECKLIST.md** for testing details
3. Review **DESIGN_SYSTEM.md** for UI/UX guidelines
4. Check logs at `infernoguard.log` for errors

---

**Happy Detecting! 🔥💨**
