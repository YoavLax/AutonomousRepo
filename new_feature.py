import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
from autonomous_agent import ExecutionLog

def export_execution_log_to_csv(db_path: str = "execution_log.db", csv_path: str = "execution_log_export.csv") -> None:
    """
    Export all execution log entries from the SQLite database to a CSV file.
    """
    if not os.path.exists(db_path):
        print(f"Database file '{db_path}' does not exist.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='execution_log';")
        if not cursor.fetchone():
            print("No 'execution_log' table found in the database.")
            return

        cursor.execute("PRAGMA table_info(execution_log);")
        columns = [col[1] for col in cursor.fetchall()]
        cursor.execute("SELECT * FROM execution_log;")
        rows = cursor.fetchall()

        if not rows:
            print("No execution log entries found.")
            return

        with open(csv_path, "w", encoding="utf-8") as f:
            f.write(",".join(columns) + "\n")
            for row in rows:
                # Escape commas and quotes in fields
                formatted = []
                for value in row:
                    if value is None:
                        formatted.append("")
                    else:
                        s = str(value)
                        if "," in s or '"' in s:
                            s = '"' + s.replace('"', '""') + '"'
                        formatted.append(s)
                f.write(",".join(formatted) + "\n")
        print(f"Exported {len(rows)} entries to '{csv_path}'.")
    finally:
        conn.close()

def new_feature():
    '''Exports the execution log from the autonomous agent to a CSV file for analysis.'''
    export_execution_log_to_csv()

if __name__ == "__main__":
    new_feature()