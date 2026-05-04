from logger import log_event, get_recent_events, get_intent_counts, get_top_commands

log_event("test123", "127.0.0.1", "whoami", "ubuntu")
log_event("test123", "127.0.0.1", "cat /etc/passwd", "fake passwd")
log_event("test123", "127.0.0.1", "chmod +x a.sh", "")

print("Recent events:")
print(get_recent_events())

print("\nIntent counts:")
print(get_intent_counts())

print("\nTop commands:")
print(get_top_commands())