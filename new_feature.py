import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
from autonomous_agent import ExecutionLog

def summarize_recent_executions(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Summarize the most recent executions from the execution log database.

    Args:
        limit (int): Number of recent executions to summarize.

    Returns:
        List[Dict[str, Any]]: List of execution summaries.
    """
    db_path = "execution_log.db"
    if not os.path.exists(db_path):
        print("No execution log database found.")
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
        summaries = []
        for row in rows:
            summaries.append({
                "id": row[0],
                "timestamp": row[1],
                "action": row[2],
                "status": row[3],
                "details": row[4]
            })
        return summaries
    finally:
        conn.close()

def print_execution_summary(limit: int = 10):
    """
    Print a summary of recent executions to the console.
    """
    summaries = summarize_recent_executions(limit)
    if not summaries:
        print("No recent executions found.")
        return
    print(f"{'ID':<5} {'Timestamp':<20} {'Action':<30} {'Status':<10} Details")
    print("-" * 80)
    for entry in summaries:
        print(f"{entry['id']:<5} {entry['timestamp']:<20} {entry['action']:<30} {entry['status']:<10} {entry['details'][:40]}")

def new_feature():
    '''Summarize and print the most recent execution log entries'''
    print_execution_summary(10)

if __name__ == "__main__":
    new_feature()