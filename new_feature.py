import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = "execution_log.db"

def get_recent_executions(limit: int = 10) -> List[Dict[str, Any]]:
    """Fetch the most recent execution log entries from the database."""
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM execution_log ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        rows = cur.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def print_recent_executions(limit: int = 10):
    """Print the most recent execution log entries in a readable format."""
    logs = get_recent_executions(limit)
    if not logs:
        print("No execution logs found.")
        return
    print(f"Showing {len(logs)} most recent executions:")
    for log in logs:
        ts = log.get("timestamp", "")
        action = log.get("action", "")
        status = log.get("status", "")
        details = log.get("details", "")
        print(f"[{ts}] Action: {action} | Status: {status} | Details: {details}")

def clear_execution_logs(confirm: bool = False):
    """Clear all execution logs from the database."""
    if not os.path.exists(DB_PATH):
        print("No execution log database found.")
        return
    if not confirm:
        print("Confirmation required to clear logs. Pass confirm=True to proceed.")
        return
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM execution_log")
        conn.commit()
        print("All execution logs have been cleared.")
    finally:
        conn.close()

def new_feature():
    """
    Feature: Execution Log Viewer & Cleaner
    - View the N most recent execution logs from the autonomous agent's database.
    - Optionally clear all logs with confirmation.
    """
    import argparse
    parser = argparse.ArgumentParser(description="Execution Log Viewer & Cleaner")
    parser.add_argument("--show", type=int, default=10, help="Show N most recent logs")
    parser.add_argument("--clear", action="store_true", help="Clear all logs (requires --yes)")
    parser.add_argument("--yes", action="store_true", help="Confirm clearing logs")
    args = parser.parse_args()

    if args.clear:
        clear_execution_logs(confirm=args.yes)
    else:
        print_recent_executions(limit=args.show)

if __name__ == "__main__":
    new_feature()