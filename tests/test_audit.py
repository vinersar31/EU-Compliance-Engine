import unittest
import os
import sqlite3
import tempfile
from eu_compliance_engine.audit import HumanOversightTracker

class TestAudit(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_human_oversight_tracker(self):
        tracker = HumanOversightTracker(self.db_path)
        tracker.log_decision("Reject Candidate", "HR_USER_123")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT ai_decision, human_reviewer_id FROM audit_logs")
        rows = cursor.fetchall()

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], "Reject Candidate")
        self.assertEqual(rows[0][1], "HR_USER_123")
        conn.close()

if __name__ == '__main__':
    unittest.main()
