import unittest
import os
import tempfile
from eu_compliance_engine.auditor import audit_codebase

class TestAuditor(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()

        with open(os.path.join(self.test_dir.name, "red_file.py"), "w") as f:
            f.write("def social_credit_score():\n    pass")

        with open(os.path.join(self.test_dir.name, "yellow_file.py"), "w") as f:
            f.write("import face_recognition\n")

        with open(os.path.join(self.test_dir.name, "blue_file.py"), "w") as f:
            f.write("def chatbot():\n    pass")

        with open(os.path.join(self.test_dir.name, "green_file.py"), "w") as f:
            f.write("def hello():\n    print('world')")

    def tearDown(self):
        self.test_dir.cleanup()

    def test_auditor(self):
        results = audit_codebase(self.test_dir.name)

        self.assertTrue(any("red_file.py" in path for path in results["FLAG RED"]))
        self.assertTrue(any("yellow_file.py" in path for path in results["FLAG YELLOW"]))
        self.assertTrue(any("blue_file.py" in path for path in results["FLAG BLUE"]))

        self.assertIn("This project is illegal in the EU.", results["report"])
        self.assertIn("Annex III High-Risk warning", results["report"])
        self.assertIn("Must label output as AI-Generated", results["report"])

if __name__ == '__main__':
    unittest.main()
