# classifier.py

import re

def classify_command(command):
    command = command.lower()

    # --- Reconnaissance ---
    if re.search(r"\b(whoami|id|uname|ls|pwd|ps|netstat)\b", command):
        return "Reconnaissance"

    # --- Exfiltration ---
    elif re.search(r"(passwd|scp|curl|wget)", command):
        return "Exfiltration"

    # --- Persistence ---
    elif re.search(r"(chmod\s+\+x|crontab|authorized_keys|systemctl)", command):
        return "Persistence"

    # --- Exploitation ---
    elif re.search(r"(sudo|bash\s+-i|nc\s|nmap|python\s+-c)", command):
        return "Exploitation"

    # --- Default ---
    else:
        return "Other"