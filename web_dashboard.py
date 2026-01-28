import os
from flask import Flask, render_template_string, request, redirect, url_for, flash, jsonify
from pathlib import Path
import subprocess
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.getenv("DASHBOARD_SECRET_KEY", "supersecret")

REPO_PATH = os.getenv("TARGET_REPO_PATH", "C:\\Users\\ylax\\source\\repos\\testgreengithub\\test")
LOG_PATH = Path(REPO_PATH) / "autonomous_agent.log"

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>GreenGitHub Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 2em; background: #f4f8f4; }
        h1 { color: #228B22; }
        .log { background: #222; color: #b6ffb6; padding: 1em; border-radius: 8px; font-size: 0.95em; max-height: 400px; overflow-y: auto; }
        .btn { background: #228B22; color: #fff; border: none; padding: 0.5em 1.5em; border-radius: 4px; cursor: pointer; }
        .btn:disabled { background: #aaa; }
        .status { margin: 1em 0; }
        .flash { color: #d32f2f; }
    </style>
</head>
<body>
    <h1>GreenGitHub Dashboard</h1>
    <div class="status">
        <b>Target Repo:</b> {{ repo_path }}<br>
        <b>Last Commit:</b> {{ last_commit or "N/A" }}<br>
        <b>Last Run:</b> {{ last_run or "N/A" }}
    </div>
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        <div class="flash">{{ messages[0] }}</div>
      {% endif %}
    {% endwith %}
    <form method="post" action="{{ url_for('run_agent') }}">
        <button class="btn" type="submit">Run Agent Now</button>
    </form>
    <h2>Recent Log</h2>
    <div class="log">{{ log_content|safe }}</div>
    <h2>Live Status</h2>
    <button class="btn" onclick="fetchStatus()">Refresh Status</button>
    <pre id="live-status" style="background:#222;color:#b6ffb6;padding:1em;border-radius:8px;"></pre>
    <script>
        function fetchStatus() {
            fetch('/api/status')
                .then(resp => resp.json())
                .then(data => {
                    document.getElementById('live-status').textContent =
                        "Agent Running: " + data.running + "\\n" +
                        "Last Commit: " + data.last_commit + "\\n" +
                        "Last Run: " + data.last_run + "\\n" +
                        "Log Tail:\\n" + data.log_tail;
                });
        }
        window.onload = fetchStatus;
    </script>
</body>
</html>
"""

def get_last_commit():
    try:
        result = subprocess.run(
            ["git", "-C", REPO_PATH, "log", "-1", "--pretty=format:%h %ad %s", "--date=short"],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except Exception:
        return None

def get_last_run_time():
    if LOG_PATH.exists():
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in reversed(lines):
            if "AUTONOMOUS COMMIT AGENT - EXECUTION STARTED" in line:
                try:
                    ts = line.split("Time:")[1].strip()
                    return ts
                except Exception:
                    continue
    return None

def get_log_content(lines=40):
    if LOG_PATH.exists():
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            log_lines = f.readlines()[-lines:]
        return "<br>".join(line.replace("<", "&lt;").replace(">", "&gt;") for line in log_lines)
    return "No log available."

def get_agent_status():
    # Check if agent process is running (simple check for demo)
    try:
        result = subprocess.run(
            ["tasklist"], capture_output=True, text=True
        )
        running = "autonomous_agent.py" in result.stdout
    except Exception:
        running = False
    return running

def get_log_tail(lines=10):
    if LOG_PATH.exists():
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            log_lines = f.readlines()[-lines:]
        return "".join(log_lines)
    return "No log available."

@app.route("/", methods=["GET"])
def dashboard():
    return render_template_string(
        DASHBOARD_TEMPLATE,
        repo_path=REPO_PATH,
        last_commit=get_last_commit(),
        last_run=get_last_run_time(),
        log_content=get_log_content()
    )

@app.route("/run", methods=["POST"])
def run_agent():
    try:
        # Run the agent once, log output to file
        with open(LOG_PATH, "a", encoding="utf-8") as logf:
            logf.write(f"\n\n=== Manual run at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
            subprocess.run(
                ["python", "autonomous_agent.py", "once"],
                cwd=Path(__file__).parent,
                stdout=logf, stderr=logf, timeout=300
            )
        flash("Agent run completed.")
    except Exception as e:
        flash(f"Error running agent: {e}")
    return redirect(url_for("dashboard"))

@app.route("/api/status", methods=["GET"])
def api_status():
    status = {
        "running": get_agent_status(),
        "last_commit": get_last_commit() or "N/A",
        "last_run": get_last_run_time() or "N/A",
        "log_tail": get_log_tail(10)
    }
    return jsonify(status)

if __name__ == "__main__":
    app.run(port=5050, debug=True)
This enhancement adds a live status API and dashboard section, allowing users to monitor agent activity, last commit, last run, and recent logs in real time.