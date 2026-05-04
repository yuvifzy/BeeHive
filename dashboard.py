from flask import Flask, render_template
from logger import get_recent_events, get_intent_counts, get_top_commands

app = Flask(__name__)

@app.route("/")
def index():
    events = get_recent_events(30)
    intent_counts = get_intent_counts()
    top_commands = get_top_commands(5)

    return render_template(
        "index.html",
        events=events,
        intent_counts=intent_counts,
        top_commands=top_commands
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000)