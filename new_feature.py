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
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, timestamp, action, status, details
            FROM execution_log
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        result = []
        for row in rows:
            result.append({
                "id": row[0],
                "timestamp": row[1],
                "action": row[2],
                "status": row[3],
                "details": row[4]
            })
        return result
    finally:
        conn.close()

def print_recent_executions(limit: int = 10):
    """Print the most recent execution log entries in a readable format."""
    logs = get_recent_executions(limit)
    if not logs:
        print("No execution logs found.")
        return
    print(f"Last {len(logs)} execution log entries:")
    for log in logs:
        print(f"[{log['timestamp']}] (ID: {log['id']}) Action: {log['action']} | Status: {log['status']}")
        if log['details']:
            print(f"  Details: {log['details']}")

def new_feature():
    '''Show the 10 most recent execution log entries from the autonomous agent's log database.'''
    print_recent_executions(10)

if __name__ == "__main__":
    new_feature()