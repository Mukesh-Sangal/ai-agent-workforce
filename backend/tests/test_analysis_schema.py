import unittest

from pydantic import ValidationError

from app.schemas.analysis import TaskAnalysis


class TaskAnalysisSchemaTests(unittest.TestCase):
    def setUp(self):
        self.data = {
            "goal": "Build a React contact form.",
            "expected_deliverable": "A reusable React form component.",
            "missing_information": ["Which fields are required?"],
        }

    def test_valid_analysis_round_trips_through_json(self):
        analysis = TaskAnalysis(**self.data)
        restored = TaskAnalysis.model_validate_json(
            analysis.model_dump_json()
        )
        self.assertEqual(restored.model_dump(), self.data)

    def test_allows_no_missing_information(self):
        analysis = TaskAnalysis(
            **{**self.data, "missing_information": []}
        )
        self.assertEqual(analysis.missing_information, [])

    def test_rejects_invalid_content(self):
        invalid_updates = [
            {"goal": ""},
            {"goal": "   "},
            {"expected_deliverable": 42},
            {"missing_information": "Unknown"},
            {"missing_information": [42]},
            {"unexpected": True},
        ]

        for update in invalid_updates:
            with self.subTest(update=update):
                with self.assertRaises(ValidationError):
                    TaskAnalysis(**{**self.data, **update})

    def test_requires_every_field(self):
        for field in self.data:
            with self.subTest(field=field):
                incomplete = self.data.copy()
                del incomplete[field]

                with self.assertRaises(ValidationError):
                    TaskAnalysis(**incomplete)