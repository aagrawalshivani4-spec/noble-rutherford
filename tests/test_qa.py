"""
Unit tests for Citizen Document Q&A RAG Engine.
"""

import unittest
from src.qa.rag_engine import DocumentQAEngine


class TestDocumentQA(unittest.TestCase):

    def setUp(self):
        with open("data/sample_documents/pm_kisan_policy.txt", "r", encoding="utf-8") as f:
            self.doc_text = f.read()
        self.qa = DocumentQAEngine(self.doc_text)

    def test_query_financial_benefit(self):
        res = self.qa.query("What is the financial benefit amount?")
        self.assertIn("answer", res)
        self.assertGreater(len(res["answer"]), 10)
        self.assertGreater(res["confidence"], 0.4)

    def test_query_in_target_language(self):
        res = self.qa.query("Who is eligible?", target_lang="hi")
        self.assertIn("answer", res)
        self.assertGreater(len(res["answer"]), 5)


if __name__ == "__main__":
    unittest.main()
