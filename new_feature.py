import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
from autonomous_agent import ExecutionLog

def summarize_execution_logs(db_path: str = "execution_log.db", limit: int = 10) -> List[Dict[str, Any]]:
    """
    Summarize the most recent execution logs from the autonomous agent.

    Args:
        db_path (str): Path to the SQLite database file.
        limit (int): Number of recent logs to summarize.

    Returns:
        List[Dict[str, Any]]: List of log summaries.
    """
    if not os.path.exists(db_path):
        print(f"Database file '{db_path}' does not exist.")
        return []

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, timestamp, action, status, details
            FROM execution_logs
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        summaries = []
        for row in rows:
            log_id, timestamp, action, status, details = row
            summaries.append({
                "id": log_id,
                "timestamp": timestamp,
                "action": action,
                "status": status,
                "details": details
            })
        return summaries
    except sqlite3.Error as e:
        print(f"Error reading logs: {e}")
        return []
    finally:
        conn.close()

def print_log_summaries(summaries: List[Dict[str, Any]]):
    if not summaries:
        print("No execution logs found.")
        return
    print(f"{'ID':<5} {'Timestamp':<20} {'Action':<30} {'Status':<10} Details")
    print("-" * 80)
    for log in summaries:
        print(f"{log['id']:<5} {log['timestamp']:<20} {log['action']:<30} {log['status']:<10} {log['details']}")

def new_feature():
    '''Summarize and print the most recent execution logs from the autonomous agent'''
    db_path = "execution_log.db"
    limit = 10
    summaries = summarize_execution_logs(db_path, limit)
    print_log_summaries(summaries)

if __name__ == "__main__":
    new_feature()