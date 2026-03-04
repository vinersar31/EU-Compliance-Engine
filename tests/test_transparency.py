import unittest
from eu_compliance_engine.transparency import inject_article_50_label

class TestTransparency(unittest.TestCase):
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

if __name__ == '__main__':
    unittest.main()
