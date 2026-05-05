# gemini_engine.py

import os
import json
import re
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

session_memory = {}


def init_session(session_id):
    if session_id not in session_memory:
        session_memory[session_id] = {
            "history": [],
            "files": {
                "backup": {"type": "dir", "content": ""},
                "logs": {"type": "dir", "content": ""},
                "config": {"type": "dir", "content": ""},
                "server.py": {
                    "type": "file",
                    "content": "# fake production service\nprint('service running')"
                }
            }
        }


def extract_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON found in Gemini response")
    return json.loads(match.group(0))


def fallback_files(session_id, intent):
    files = session_memory[session_id]["files"]

    if intent == "Reconnaissance":
        files["app_config.json"] = {
            "type": "file",
            "content": '{ "env": "production", "debug": false, "db_host": "internal-db.local" }'
        }

    elif intent == "Exfiltration":
        files["customer_backup_sample.sql"] = {
            "type": "file",
            "content": "-- fake database backup\nINSERT INTO users VALUES (1, 'demo_user', 'fake_hash');"
        }

    elif intent == "Persistence":
        files["maintenance_cron.txt"] = {
            "type": "file",
            "content": "0 2 * * * /home/ubuntu/scripts/backup.sh"
        }

    elif intent == "Exploitation":
        files["sudo_policy_notes.txt"] = {
            "type": "file",
            "content": "Temporary note: restricted service restart permissions under review."
        }


def generate_fake_files(session_id, command, intent):
    init_session(session_id)

    memory = session_memory[session_id]
    memory["history"].append({
        "command": command,
        "intent": intent
    })

    prompt = f"""
You are an AI deception engine for a defensive SSH honeypot.

Generate fake Linux server files to keep an attacker engaged.

SAFETY RULES:
- Do not generate real secrets.
- Do not generate malware.
- Do not generate exploit instructions.
- All credentials must be obviously fake.
- Content should be believable but harmless.

Recent attacker behavior:
{json.dumps(memory["history"][-8:], indent=2)}

Existing fake files:
{list(memory["files"].keys())}

Latest command:
{command}

Detected intent:
{intent}

Return ONLY valid JSON in this exact structure:
{{
  "new_files": [
    {{
      "filename": "example.txt",
      "type": "file",
      "content": "fake harmless content"
    }}
  ]
}}

Generate 1 to 3 useful fake files.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        data = extract_json(response.text)

        for item in data.get("new_files", []):
            filename = item.get("filename")
            file_type = item.get("type", "file")
            content = item.get("content", "")

            if filename:
                memory["files"][filename] = {
                    "type": file_type,
                    "content": content
                }

        print(f"[AI] Generated files for {session_id}")

    except Exception as e:
        print("[AI ERROR] Using fallback:", e)
        fallback_files(session_id, intent)


def list_files(session_id):
    init_session(session_id)
    return "  ".join(session_memory[session_id]["files"].keys()) + "\n"


def read_file(session_id, filename):
    init_session(session_id)

    files = session_memory[session_id]["files"]

    if filename in files:
        item = files[filename]

        if item["type"] == "dir":
            return f"cat: {filename}: Is a directory\n"

        return item["content"] + "\n"

    return f"cat: {filename}: Permission Denied\n"