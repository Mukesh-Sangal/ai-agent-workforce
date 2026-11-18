import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.summary import TaskSummary
from app.services.summary_service import (
    SummaryError,
    SummaryTimeout,
    SummaryUnavailable,
)


class SummaryRouteTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.addCleanup(self.client.close)

    @patch("app.api.routes.generate_task_summary")
    def test_valid_request_returns_summary(self, generate):
        # Synthetic output: this test does not contact OpenAI.
        result = TaskSummary(
            response_id="resp_test",
            summary="Build an accessible React contact form.",
            model="test-model",
        )
        generate.return_value = result

        response = self.client.post(
            "/task-summaries",
            json={"description": "Build an accessible React contact form."},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), result.model_dump(mode="json"))
        generate.assert_called_once()

        task = generate.call_args.args[0]
        self.assertEqual(
            task.description,
            "Build an accessible React contact form.",
        )

    @patch("app.api.routes.generate_task_summary")
    def test_blank_description_never_calls_service(self, generate):
        response = self.client.post(
            "/task-summaries",
            json={"description": ""},
        )

        self.assertEqual(response.status_code, 422)
        generate.assert_not_called()

    @patch("app.api.routes.generate_task_summary")
    def test_service_errors_return_expected_status(self, generate):
        cases = [
            (SummaryTimeout("The model request timed out."), 504),
            (SummaryUnavailable("Model service unavailable."), 503),
            (SummaryError("The model request failed."), 502),
        ]

        for error, expected_status in cases:
            with self.subTest(error=type(error).__name__):
                generate.side_effect = error

                response = self.client.post(
                    "/task-summaries",
                    json={
                        "description": "Build an accessible React contact form."
                    },
                )

                self.assertEqual(response.status_code, expected_status)
                self.assertEqual(
                    response.json(),
                    {"detail": str(error)},
                )