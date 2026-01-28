# ... (existing imports and code above remain unchanged)

from flask import Flask, jsonify, request
import threading

# ... (existing code above remains unchanged)

app = Flask(__name__)

status_info = {
    "enabled": AUTONOMOUS_AGENT_ENABLED,
    "target_repo": TARGET_REPO_PATH,
    "scheduled_times": COMMIT_TIMES,
    "last_commit": None,
    "last_commit_status": None,
    "next_runs": []
}

def get_next_runs():
    # Returns a list of next scheduled run times as strings
    try:
        loop = asyncio.get_event_loop()
        scheduler = AsyncIOScheduler(event_loop=loop)
        for time_str in COMMIT_TIMES:
            hour, minute = map(int, time_str.split(":"))
            trigger = CronTrigger(hour=hour, minute=minute)
            scheduler.add_job(lambda: None, trigger=trigger, id=f"commit_{time_str}")
        scheduler.start()
        runs = []
        for job in scheduler.get_jobs():
            if job.next_run_time:
                runs.append(f"{job.id}: {job.next_run_time.strftime('%Y-%m-%d %H:%M:%S')}")
        scheduler.shutdown()
        return runs
    except Exception:
        return []

@app.route("/status", methods=["GET"])
def status():
    status_info["next_runs"] = get_next_runs()
    return jsonify(status_info)

@app.route("/run-once", methods=["POST"])
def run_once_api():
    if not AUTONOMOUS_AGENT_ENABLED:
        return jsonify({"error": "Agent is disabled"}), 400
    def run_commit():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(make_autonomous_commit(TARGET_REPO_PATH))
        status_info["last_commit_status"] = "success" if result else "failure"
    t = threading.Thread(target=run_commit)
    t.start()
    return jsonify({"message": "Autonomous commit triggered"}), 202

@app.route("/recent-commits", methods=["GET"])
def recent_commits():
    try:
        from git import Repo
        repo = Repo(TARGET_REPO_PATH)
        commits = []
        for c in repo.iter_commits('main', max_count=5):
            commits.append({
                "hash": c.hexsha[:8],
                "message": c.message.strip(),
                "date": c.committed_datetime.strftime("%Y-%m-%d %H:%M:%S")
            })
        return jsonify(commits)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def start_dashboard():
    print("🌐 Starting web dashboard at http://localhost:5000 ...")
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "once":
        asyncio.run(run_once())
    elif len(sys.argv) > 1 and sys.argv[1] == "dashboard":
        start_dashboard()
    else:
        start_scheduler()

This adds a web dashboard with `/status`, `/run-once`, and `/recent-commits` endpoints. Start it with `python autonomous_agent.py dashboard`.