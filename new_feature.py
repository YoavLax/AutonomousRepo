import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = "execution_log.db"

def get_recent_executions(limit: int = 10) -> List[Dict[str, Any]]:
    """Fetch the most recent execution log entries from the database."""
    if not os.path.exists(DB_PATH):
        print("No execution log database found.")
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
        print("No recent executions found.")
        return
    print(f"Showing {len(logs)} most recent executions:")
    for log in logs:
        ts = log.get("timestamp", "")
        action = log.get("action", "")
        status = log.get("status", "")
        details = log.get("details", "")
        print(f"[{ts}] Action: {action} | Status: {status} | Details: {details}")

def new_feature():
    '''Show the 10 most recent autonomous agent executions from the log database.'''
    print_recent_executions(10)

if __name__ == "__main__":
    new_feature()