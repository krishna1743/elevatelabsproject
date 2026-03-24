# 🔐 Password Security Toolkit

A modern, professional cybersecurity utility for **password strength analysis** and **custom wordlist generation** — built with Python and PySide6.

---

## 📸 Screenshots

> *(Run the app and take your own screenshots to place here)*
> 
> `assets/screenshots/dashboard.png`  
> `assets/screenshots/analyzer.png`  
> `assets/screenshots/wordlist.png`  

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 Password Analyzer | Score (0–4), entropy in bits, estimated crack time, weakness patterns |
| 📊 Strength Meter | Color-coded progress bar (red → orange → green) |
| 📋 Wordlist Generator | Targeted wordlists from personal info with leet-speak & suffix variations |
| 📄 Report Generator | Formatted text reports saved to `/output/` |
| 🌗 Theme Toggle | Dark / Light mode via Settings page |
| 📝 Logging | All actions logged to `/logs/activity.log` |

---

## 🗂 Project Structure

```
password_security_toolkit/
├── main.py                  # Entry point — sets up logging, launches GUI
├── gui_main.py              # PySide6 GUI — sidebar, stacked pages, styles
├── password_analyzer.py     # Core analysis engine (zxcvbn + custom)
├── entropy_calculator.py    # Shannon entropy calculator
├── wordlist_generator.py    # Wordlist builder with itertools.product
├── leetspeak.py             # Leet-speak character substitutions
├── report_generator.py      # Text report formatter
├── requirements.txt
├── README.md
├── assets/
│   └── icons/              # (optional) icon files
├── output/
│   ├── wordlist.txt        # Generated wordlists
│   └── password_report.txt # Latest analysis report
└── logs/
    └── activity.log        # Application log
```

---

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- pip

### Steps

```bash
# 1. Clone or download the project
cd password_security_toolkit

# 2. (Recommended) Create a virtual environment
python -m venv venv
source venv/bin/activate       # Linux / macOS
venv\Scripts\activate.bat      # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python main.py
```

---

## 🧪 Usage

### Password Analyzer
1. Click **Analyzer** in the sidebar.
2. Type or paste any password.
3. Click **Analyze Password**.
4. Review the strength score, entropy, crack time, and recommendations.

### Wordlist Generator
1. Click **Wordlist** in the sidebar.
2. Fill in personal details (any combination of fields).
3. Click **Generate Wordlist** → then **Preview** or **Export**.

### Reports
1. Run an analysis first (Analyzer page).
2. Navigate to **Reports** → **Generate Report**.
3. Optionally **Save to File**.

### Settings
- Toggle **Dark / Light Theme**.
- Change the **Export Directory**.
- **Clear Log File** to reset activity.log.

---

## 🧪 Test Data

### Sample passwords to test:

| Password | Expected Score | Notes |
|---|---|---|
| `abc` | 0 | Very Weak — too short |
| `password123` | 1 | Weak — dictionary word |
| `MyDog2024!` | 2–3 | Fair — mixed but predictable |
| `Tr0ub4dor&3` | 3–4 | Strong — mixed random |
| `correcthorsebatterystaple` | 3–4 | Strong — long passphrase |

### Sample wordlist user data:

```
First Name : john
Last Name  : smith
Pet Name   : buddy
Birth Year : 1990
Fav Number : 7
City       : london
```

Expected output includes: `john1990`, `Buddy@123`, `sm1th2024`, `l0nd0n7`, etc.

---

## 🔒 Security Disclaimer

> ⚠️ **Educational use only.**  
> This tool is designed for learning about password security, evaluating your own passwords, and understanding how wordlists are generated.  
> Do **not** use this tool on systems or accounts you do not own or have explicit written permission to test.  
> Misuse of this tool may violate computer fraud laws in your jurisdiction.

---

## 🔮 Future Improvements

- [ ] Hash cracking simulation (MD5, SHA-1, SHA-256)
- [ ] Integration with HaveIBeenPwned API for breach detection
- [ ] Password policy compliance checker (e.g. NIST SP 800-63B)
- [ ] Batch password analysis from CSV
- [ ] Passphrase generator (EFF wordlist)
- [ ] Export report as PDF

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `PySide6` | Modern Qt GUI framework |
| `zxcvbn` | Realistic password strength estimation |

---

## 👨‍💻 Author

Built as a professional cybersecurity portfolio project.  
Demonstrates: Python, PySide6 GUI, modular architecture, security concepts.
