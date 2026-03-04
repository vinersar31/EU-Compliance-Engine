import sqlite3
import datetime

class HumanOversightTracker:
    def __init__(self, db_path: str = "audit_logs.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ai_decision TEXT NOT NULL,
                human_reviewer_id TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def log_decision(self, ai_decision: str, human_reviewer_id: str):
        """
        Logs a high-stakes AI decision and the human reviewer to the database.
        """
        timestamp = datetime.datetime.now().isoformat()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO audit_logs (ai_decision, human_reviewer_id, timestamp)
            VALUES (?, ?, ?)
        ''', (ai_decision, human_reviewer_id, timestamp))
        conn.commit()
        conn.close()
