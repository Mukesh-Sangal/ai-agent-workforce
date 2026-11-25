import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.analysis import TaskAnalysis
from app.services.analysis_service import (
    AnalysisError,
    AnalysisRefused,
    AnalysisTimeout,
    AnalysisUnavailable,
)


class AnalysisRouteTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.addCleanup(self.client.close)

    @patch("app.api.routes.generate_task_analysis")
    def test_valid_request_returns_structured_analysis(self, generate):
        result = TaskAnalysis(
            goal="Build a React contact form.",
            expected_deliverable="A reusable React component.",
            missing_information=["Which fields are required?"],
        )
        generate.return_value = result

        response = self.client.post(
            "/task-analyses",
            json={"description": "  Build a React contact form.  "},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            result.model_dump(mode="json"),
        )
        generate.assert_called_once()

        task = generate.call_args.args[0]
        self.assertEqual(
            task.description,
            "Build a React contact form.",
        )

    @patch("app.api.routes.generate_task_analysis")
    def test_invalid_input_never_calls_service(self, generate):
        invalid_bodies = [
            {},
            {"description": ""},
            {"description": "short"},
            {"description": 1234567890},
            {
                "description": "Build a contact form.",
                "unexpected": True,
            },
        ]

        for body in invalid_bodies:
            with self.subTest(body=body):
                response = self.client.post(
                    "/task-analyses",
                    json=body,
                )
                self.assertEqual(response.status_code, 422)

        generate.assert_not_called()

    @patch("app.api.routes.generate_task_analysis")
    def test_service_errors_return_expected_status(self, generate):
        cases = [
            (AnalysisTimeout("Request timed out."), 504),
            (AnalysisUnavailable("Service unavailable."), 503),
            (AnalysisRefused("Analysis declined."), 422),
            (AnalysisError("Analysis failed."), 502),
        ]

        for error, expected_status in cases:
            with self.subTest(error=type(error).__name__):
                generate.side_effect = error

                response = self.client.post(
                    "/task-analyses",
                    json={
                        "description": "Build a React contact form."
                    },
                )

                self.assertEqual(
                    response.status_code,
                    expected_status,
                )
                self.assertEqual(
                    response.json(),
                    {"detail": str(error)},
                )