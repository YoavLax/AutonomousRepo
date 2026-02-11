import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional

def get_log_db_path() -> str:
    """Get the path to the execution log database, matching autonomous_agent.py logic."""
    return os.getenv("EXEC_LOG_DB_PATH", "execution_log.db")

def fetch_recent_executions(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch the most recent execution log entries from the SQLite database.

    Args:
        limit (int): Number of recent entries to fetch.

    Returns:
        List[Dict[str, Any]]: List of execution log entries.
    """
    db_path = get_log_db_path()
    if not os.path.exists(db_path):
        return []

    conn = sqlite3.connect(db_path)
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
    """
    Print the most recent execution log entries in a readable format.
    """
    entries = fetch_recent_executions(limit)
    if not entries:
        print("No execution log entries found.")
        return

    print(f"Showing {len(entries)} most recent execution log entries:\n")
    for entry in entries:
        timestamp = entry.get("timestamp", "")
        action = entry.get("action", "")
        status = entry.get("status", "")
        details = entry.get("details", "")
        print(f"[{timestamp}] Action: {action} | Status: {status}")
        if details:
            print(f"  Details: {details}")
        print("-" * 60)

def new_feature():
    '''Display the 10 most recent execution log entries from the autonomous agent.'''
    print_recent_executions(10)

if __name__ == "__main__":
    new_feature()