import unittest
import os
from fastapi.testclient import TestClient
from eu_compliance_engine.api import app

class TestAPICORS(unittest.TestCase):
    def setUp(self):
        # We need to re-initialize the app or middleware if we want to test different env vars
        # but for now, we'll test the current state of the app.
        self.client = TestClient(app)

    def test_cors_allowed_origin(self):
        # Default allowed origin is http://localhost:3000
        response = self.client.options(
            "/evaluate",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "http://localhost:3000")

    def test_cors_disallowed_origin(self):
        response = self.client.options(
            "/evaluate",
            headers={
                "Origin": "http://malicious.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )
        # For disallowed origins, FastAPI's CORSMiddleware either returns a 400 or a 200 without the CORS headers
        # or it might just not include the Access-Control-Allow-Origin header.
        self.assertNotEqual(response.headers.get("Access-Control-Allow-Origin"), "http://malicious.com")
        self.assertIsNone(response.headers.get("Access-Control-Allow-Origin"))

if __name__ == "__main__":
    unittest.main()
