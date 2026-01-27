import os
from flask import Flask, render_template_string, request, redirect, url_for, flash
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

if __name__ == "__main__":
    app.run(port=5050, debug=True)
This dashboard lets users monitor commit activity, view logs, and trigger the agent manually, greatly improving usability and transparency.