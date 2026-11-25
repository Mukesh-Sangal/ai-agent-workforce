import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx2
from openai import OpenAI as RealOpenAI

from app.schemas.analysis import TaskAnalysis
from app.schemas.task import TaskRequest
from app.services import analysis_service as service


def provider_response(
    status="completed",
    text=None,
    refusal=False,
):
    data = {
        "goal": "Build a contact form.",
        "expected_deliverable": "A React form component.",
        "missing_information": [
            "Which fields are required?"
        ],
    }

    content = [
        {
            "type": "output_text",
            "text": (
                json.dumps(data)
                if text is None
                else text
            ),
            "annotations": [],
        }
    ]

    if refusal:
        content = [
            {
                "type": "refusal",
                "refusal": "Simulated provider refusal.",
            }
        ]

    return {
        "id": "resp_test_analysis",
        "object": "response",
        "created_at": 1,
        "status": status,
        "model": "test-model",
        "output": [
            {
                "type": "message",
                "id": "msg_test",
                "role": "assistant",
                "status": "completed",
                "content": content,
            }
        ],
    }


class AnalysisServiceTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)

        self.env = Path(tmp.name) / ".env"
        self.env.write_text(
            "OPENAI_API_KEY=fake-key\n"
            "OPENAI_MODEL=test-model\n"
        )

        for patcher in (
            patch.dict(os.environ, {}, clear=True),
            patch.object(service, "ENV_FILE", self.env),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)

        self.requests = []

    def call(
        self,
        payload=None,
        status=200,
        timeout=False,
        connection_error=False,
    ):
        def handler(request):
            self.requests.append(request)

            if timeout:
                raise httpx2.ReadTimeout(
                    "Simulated timeout",
                    request=request,
                )

            if connection_error:
                raise httpx2.ConnectError(
                    "Simulated connection failure",
                    request=request,
                )

            return httpx2.Response(
                status,
                json=payload,
                request=request,
            )

        def client(**kwargs):
            transport = httpx2.MockTransport(handler)

            return RealOpenAI(
                **kwargs,
                http_client=httpx2.Client(
                    transport=transport
                ),
            )

        with patch.object(
            service,
            "OpenAI",
            side_effect=client,
        ):
            return service.generate_task_analysis(
                TaskRequest(
                    description="Build a React contact form."
                )
            )

    def test_success_parses_real_sdk_and_sends_strict_schema(self):
        result = self.call(provider_response())

        self.assertIsInstance(result, TaskAnalysis)
        self.assertEqual(
            result.missing_information,
            ["Which fields are required?"],
        )

        sent = json.loads(self.requests[0].content)

        self.assertEqual(
            sent["input"],
            "Build a React contact form.",
        )
        self.assertEqual(sent["model"], "test-model")
        self.assertFalse(sent["store"])

        output_format = sent["text"]["format"]

        self.assertEqual(
            output_format["type"],
            "json_schema",
        )
        self.assertTrue(output_format["strict"])
        self.assertFalse(
            output_format["schema"]["additionalProperties"]
        )
        self.assertEqual(len(self.requests), 1)

    def test_missing_configuration_never_constructs_client(self):
        self.env.write_text("")

        with patch.object(service, "OpenAI") as client:
            with self.assertRaises(
                service.AnalysisUnavailable
            ):
                service.generate_task_analysis(
                    TaskRequest(
                        description="Review the contact form."
                    )
                )

        client.assert_not_called()

    def test_timeout_is_explicit_and_not_retried(self):
        with self.assertRaises(service.AnalysisTimeout):
            self.call(timeout=True)

        self.assertEqual(len(self.requests), 1)

    def test_rate_limit_is_explicit_and_not_retried(self):
        payload = {
            "error": {
                "message": "Rate limited",
                "type": "rate_limit_error",
            }
        }

        with self.assertRaises(service.AnalysisUnavailable):
            self.call(payload, status=429)

        self.assertEqual(len(self.requests), 1)

    def test_provider_error_has_safe_message(self):
        payload = {
            "error": {
                "message": "fake-key rejected",
                "type": "invalid_api_key",
            }
        }

        with self.assertRaises(
            service.AnalysisError
        ) as caught:
            self.call(payload, status=401)

        self.assertNotIn(
            "fake-key",
            str(caught.exception),
        )

    def test_refusal_is_not_success(self):
        with self.assertRaises(service.AnalysisRefused):
            self.call(provider_response(refusal=True))

    def test_incomplete_output_is_not_success(self):
        with self.assertRaises(service.AnalysisError):
            self.call(
                provider_response(status="incomplete")
            )

    def test_invalid_schema_data_is_not_success(self):
        with self.assertRaises(service.AnalysisError):
            self.call(
                provider_response(
                    text='{"goal": "Build a form"}'
                )
            )

    def test_connection_error_is_mapped(self):
        with self.assertRaises(service.AnalysisError):
            self.call(connection_error=True)

    def test_missing_parsed_output_is_not_success(self):
        payload = provider_response()
        payload["output"] = []

        with self.assertRaises(service.AnalysisError):
            self.call(payload)