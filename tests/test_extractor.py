"""
Unit tests for Key Information Extractor.
"""

import unittest
from src.extraction.extractor import KeyInformationExtractor


class TestExtractor(unittest.TestCase):

    def setUp(self):
        with open("data/sample_documents/pmay_scheme.txt", "r", encoding="utf-8") as f:
            self.pmay_text = f.read()
        with open("data/sample_documents/pm_kisan_policy.txt", "r", encoding="utf-8") as f:
            self.kisan_text = f.read()

    def test_pmay_extraction(self):
        res = KeyInformationExtractor.extract_all(self.pmay_text)
        self.assertIn("pradhan mantri awas yojana", res["scheme_name"].lower())
        self.assertEqual(res["abbreviation"], "PMAY")
        self.assertIn("housing", res["ministry"].lower())
        self.assertIn("2025", str(res["target_year"]))
        self.assertGreater(res["entity_count"], 5)
        self.assertTrue(any("Aadhaar" in doc for doc in res["required_documents"]))

    def test_kisan_extraction(self):
        res = KeyInformationExtractor.extract_all(self.kisan_text)
        self.assertIn("pm-kisan", res["scheme_name"].lower())
        self.assertIn("agriculture", res["ministry"].lower())
        self.assertIn("6,000", res["benefits"])


if __name__ == "__main__":
    unittest.main()
