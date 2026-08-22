"""
Unit tests for Summarization Sub-system.
"""

import unittest
from src.summarization.summarizer import DocumentSummarizer


class TestSummarizer(unittest.TestCase):

    def setUp(self):
        self.summarizer = DocumentSummarizer()
        with open("data/sample_documents/pmay_scheme.txt", "r", encoding="utf-8") as f:
            self.sample_text = f.read()

    def test_summarization_output_structure(self):
        res = self.summarizer.summarize(self.sample_text, max_length=120)
        self.assertIn("executive_summary", res)
        self.assertIn("bullet_points", res)
        self.assertIn("compression_ratio", res)
        self.assertGreater(len(res["executive_summary"]), 30)
        self.assertGreaterEqual(len(res["bullet_points"]), 1)
        self.assertGreater(res["original_word_count"], res["summary_word_count"])

    def test_short_text_passthrough(self):
        short = "This is a brief circular."
        res = self.summarizer.summarize(short)
        self.assertEqual(res["executive_summary"], short)


if __name__ == "__main__":
    unittest.main()
