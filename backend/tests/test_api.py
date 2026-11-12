import unittest
from uuid import UUID

from fastapi.testclient import TestClient

from app.main import app


class TaskApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.addCleanup(self.client.close)

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_valid_preview(self):
        description = "Research accessible contact form patterns."
        response = self.client.post(
            "/task-previews", json={"description": description}
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        UUID(body["id"])
        self.assertEqual(body["description"], description)
        self.assertEqual(body["status"], "preview_only")
        self.assertIs(body["model_called"], False)

    def test_trims_whitespace(self):
        response = self.client.post(
            "/task-previews", json={"description": "  Review this contact form.  "}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["description"], "Review this contact form.")

    def test_rejects_blank_description(self):
        response = self.client.post("/task-previews", json={"description": " " * 20})
        self.assertEqual(response.status_code, 422)

    def test_rejects_short_description(self):
        response = self.client.post("/task-previews", json={"description": "short"})
        self.assertEqual(response.status_code, 422)

    def test_rejects_oversized_description(self):
        response = self.client.post("/task-previews", json={"description": "a" * 2001})
        self.assertEqual(response.status_code, 422)

    def test_rejects_missing_description(self):
        response = self.client.post("/task-previews", json={})
        self.assertEqual(response.status_code, 422)

    def test_rejects_unknown_fields(self):
        response = self.client.post(
            "/task-previews", json={"description": "Review this contact form.", "admin": True}
        )
        self.assertEqual(response.status_code, 422)

    def test_rejects_non_string_description(self):
        response = self.client.post("/task-previews", json={"description": 1234567890})
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
