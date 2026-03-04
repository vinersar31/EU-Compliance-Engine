import unittest
import os
import sqlite3
import tempfile
from eu_compliance_engine.auditor import audit_codebase
from eu_compliance_engine.transparency import inject_article_50_label
from eu_compliance_engine.audit import HumanOversightTracker

class TestNewFeatures(unittest.TestCase):
    def setUp(self):
        # Setup for Auditor test
        self.test_dir = tempfile.TemporaryDirectory()

        with open(os.path.join(self.test_dir.name, "red_file.py"), "w") as f:
            f.write("def social_credit_score():\n    pass")

        with open(os.path.join(self.test_dir.name, "yellow_file.py"), "w") as f:
            f.write("import face_recognition\n")

        with open(os.path.join(self.test_dir.name, "blue_file.py"), "w") as f:
            f.write("def chatbot():\n    pass")

        with open(os.path.join(self.test_dir.name, "green_file.py"), "w") as f:
            f.write("def hello():\n    print('world')")

        # Setup for Tracker test
        self.db_fd, self.db_path = tempfile.mkstemp()

    def tearDown(self):
        self.test_dir.cleanup()
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_auditor(self):
        results = audit_codebase(self.test_dir.name)

        self.assertTrue(any("red_file.py" in path for path in results["FLAG RED"]))
        self.assertTrue(any("yellow_file.py" in path for path in results["FLAG YELLOW"]))
        self.assertTrue(any("blue_file.py" in path for path in results["FLAG BLUE"]))

        self.assertIn("This project is illegal in the EU.", results["report"])
        self.assertIn("Annex III High-Risk warning", results["report"])
        self.assertIn("Must label output as AI-Generated", results["report"])

    def test_transparency(self):
        headers = {"content-type": "application/json"}
        updated_headers = inject_article_50_label(headers)

        self.assertIn("x-ai-generated", updated_headers)
        self.assertEqual(updated_headers["x-ai-generated"], "true")
        self.assertEqual(updated_headers["content-type"], "application/json")

        # Test with None
        updated_headers_none = inject_article_50_label(None)
        self.assertIn("x-ai-generated", updated_headers_none)
        self.assertEqual(updated_headers_none["x-ai-generated"], "true")

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
