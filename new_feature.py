import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional

from autonomous_agent import ExecutionLog

def get_recent_executions(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Retrieve the most recent execution log entries from the database.
    """
    db_path = "execution_log.db"
    if not os.path.exists(db_path):
        return []
    conn = sqlite3.connect(db_path)
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
    """
    Print the most recent execution log entries in a readable format.
    """
    entries = get_recent_executions(limit)
    if not entries:
        print("No execution log entries found.")
        return
    print(f"Last {len(entries)} execution log entries:")
    for entry in entries:
        print(f"[{entry['timestamp']}] (ID: {entry['id']}) {entry['action']} - {entry['status']}")
        if entry['details']:
            print(f"  Details: {entry['details']}")

def log_custom_action(action: str, status: str, details: Optional[str] = None):
    """
    Log a custom action to the execution log.
    """
    log = ExecutionLog()
    log.log_action(action, status, details or "")

def new_feature():
    '''Feature: View and log recent execution actions for the autonomous agent'''
    import argparse
    parser = argparse.ArgumentParser(description="Execution Log Utility")
    parser.add_argument("--show", action="store_true", help="Show recent execution log entries")
    parser.add_argument("--log", nargs=2, metavar=("ACTION", "STATUS"), help="Log a custom action with status")
    parser.add_argument("--details", type=str, default="", help="Details for the custom log action")
    parser.add_argument("--limit", type=int, default=10, help="Number of entries to show")
    args = parser.parse_args()

    if args.show:
        print_recent_executions(args.limit)
    elif args.log:
        action, status = args.log
        log_custom_action(action, status, args.details)
        print(f"Logged action '{action}' with status '{status}'.")
    else:
        parser.print_help()

if __name__ == "__main__":
    new_feature()