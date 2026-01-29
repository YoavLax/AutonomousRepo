import sqlite3
import threading
from typing import Optional, Dict, Any, List
import datetime

class ExecutionLog:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_path: str = "execution_log.db"):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init_db(db_path)
            return cls._instance

    def _init_db(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._create_tables()

    def _create_tables(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    status TEXT NOT NULL,
                    files_changed TEXT,
                    improvement_type TEXT,
                    copilot_response_time REAL,
                    error_message TEXT
                )
            """)

    def log_execution(self, status: str, files_changed: Optional[str], improvement_type: Optional[str],
                      copilot_response_time: Optional[float], error_message: Optional[str]):
        with self.conn:
            self.conn.execute("""
                INSERT INTO executions (timestamp, status, files_changed, improvement_type, copilot_response_time, error_message)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                datetime.datetime.utcnow().isoformat(),
                status,
                files_changed,
                improvement_type,
                copilot_response_time,
                error_message
            ))

    def get_recent_executions(self, limit: int = 100) -> List[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute("""
            SELECT timestamp, status, files_changed, improvement_type, copilot_response_time, error_message
            FROM executions
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        rows = cur.fetchall()
        return [
            {
                "timestamp": row[0],
                "status": row[1],
                "files_changed": row[2],
                "improvement_type": row[3],
                "copilot_response_time": row[4],
                "error_message": row[5]
            }
            for row in rows
        ]

    def get_stats(self) -> Dict[str, Any]:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM executions WHERE status = 'success'")
        success_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM executions WHERE status = 'failure'")
        failure_count = cur.fetchone()[0]
        cur.execute("SELECT AVG(copilot_response_time) FROM executions WHERE copilot_response_time IS NOT NULL")
        avg_response = cur.fetchone()[0]
        return {
            "success_count": success_count,
            "failure_count": failure_count,
            "avg_copilot_response_time": avg_response
        }

import os
from flask import Flask, render_template_string, send_from_directory
from execution_log import ExecutionLog

app = Flask(__name__)

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>GreenGitHub Execution Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 2em; background: #f7f7f7; }
        h1 { color: #2c7a7b; }
        table { border-collapse: collapse; width: 100%; background: #fff; }
        th, td { border: 1px solid #ddd; padding: 8px; }
        th { background: #2c7a7b; color: #fff; }
        tr:nth-child(even) { background: #f2f2f2; }
        .success { color: green; }
        .failure { color: red; }
        .stats { margin-bottom: 2em; }
    </style>
</head>
<body>
    <h1>GreenGitHub Execution Dashboard</h1>
    <div class="stats">
        <strong>Successes:</strong> {{ stats.success_count }} |
        <strong>Failures:</strong> {{ stats.failure_count }} |
        <strong>Avg Copilot Response (s):</strong> {{ "%.2f"|format(stats.avg_copilot_response_time or 0) }}
    </div>
    <table>
        <tr>
            <th>Timestamp</th>
            <th>Status</th>
            <th>Files Changed</th>
            <th>Improvement Type</th>
            <th>Copilot Response (s)</th>
            <th>Error Message</th>
        </tr>
        {% for row in executions %}
        <tr>
            <td>{{ row.timestamp }}</td>
            <td class="{{ row.status }}">{{ row.status }}</td>
            <td>{{ row.files_changed or "" }}</td>
            <td>{{ row.improvement_type or "" }}</td>
            <td>{{ "%.2f"|format(row.copilot_response_time or 0) }}</td>
            <td>{{ row.error_message or "" }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

@app.route("/")
def dashboard():
    log = ExecutionLog()
    executions = log.get_recent_executions(100)
    stats = log.get_stats()
    return render_template_string(DASHBOARD_TEMPLATE, executions=executions, stats=stats)

if __name__ == "__main__":
    app.run(port=8080, debug=True)

[...existing code...]

# --- Add these imports at the top ---
from execution_log import ExecutionLog

# --- In the main agent logic, after each commit attempt (success or failure), add: ---
# Example usage:
# log = ExecutionLog()
# log.log_execution(
#     status="success" or "failure",
#     files_changed="comma,separated,files",
#     improvement_type="feature|refactor|docs|etc",
#     copilot_response_time=seconds_float,
#     error_message="error details if any"
# )

# Place this in the appropriate try/except/finally blocks where commits are made.

# --- End of addition ---