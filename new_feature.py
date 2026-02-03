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
    logs = get_recent_executions(limit)
    if not logs:
        print("No execution logs found.")
        return
    print(f"Showing {len(logs)} most recent executions:")
    for log in logs:
        print(f"[{log['timestamp']}] (ID: {log['id']}) Action: {log['action']} | Status: {log['status']}")
        if log['details']:
            print(f"    Details: {log['details']}")

def clear_execution_logs(confirm: bool = False):
    """
    Clear all execution logs from the database.
    """
    if not confirm:
        print("Confirmation required to clear logs. Pass confirm=True to proceed.")
        return
    db_path = "execution_log.db"
    if not os.path.exists(db_path):
        print("No execution log database found.")
        return
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM execution_log")
        conn.commit()
        print("All execution logs have been cleared.")
    finally:
        conn.close()

def new_feature():
    '''Provides a CLI utility to view and clear recent execution logs from the autonomous agent'''
    import argparse
    parser = argparse.ArgumentParser(description="Execution Log Utility")
    parser.add_argument("--show", action="store_true", help="Show recent execution logs")
    parser.add_argument("--limit", type=int, default=10, help="Number of recent logs to show")
    parser.add_argument("--clear", action="store_true", help="Clear all execution logs (requires --yes)")
    parser.add_argument("--yes", action="store_true", help="Confirm clearing logs")
    args = parser.parse_args()

    if args.show:
        print_recent_executions(args.limit)
    elif args.clear:
        clear_execution_logs(confirm=args.yes)
    else:
        parser.print_help()

if __name__ == "__main__":
    new_feature()