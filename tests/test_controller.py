"""
Unit tests for Agentic AI Controller & Workflow Execution.
"""

import unittest
from src.agent.controller import AgenticNLPController


class TestAgenticController(unittest.TestCase):

    def setUp(self):
        self.controller = AgenticNLPController()
        with open("data/sample_documents/pmay_scheme.txt", "r", encoding="utf-8") as f:
            self.sample_doc = f.read()

    def test_full_pipeline_execution(self):
        state = self.controller.execute_workflow(
            document_input=self.sample_doc,
            filename="pmay_test.txt",
            target_language="hi"
        )
        self.assertEqual(state.status, "COMPLETED")
        self.assertGreater(len(state.agent_trace), 5)
        self.assertEqual(state.source_language_code, "en")
        self.assertEqual(state.target_language_code, "hi")
        self.assertGreater(len(state.executive_summary), 20)
        self.assertGreater(len(state.translated_summary), 10)
        self.assertIn("pradhan mantri awas yojana", state.extracted_entities.get("scheme_name", "").lower())
        self.assertGreater(state.total_latency_sec, 0.0)


if __name__ == "__main__":
    unittest.main()
