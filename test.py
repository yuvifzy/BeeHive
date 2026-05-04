from logger import log_event, get_recent_events, get_intent_counts

log_event("session1", "127.0.0.1", "whoami", "ubuntu")
log_event("session1", "127.0.0.1", "cat /etc/passwd", "fake passwd file")

print(get_recent_events())
print(get_intent_counts())