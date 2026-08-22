"""
Unit tests for NLP Accuracy and Evaluation Metrics.
"""

import unittest
from src.metrics.evaluator import NLPAccuracyEvaluator


class TestAccuracyMetrics(unittest.TestCase):

    def setUp(self):
        self.ref_doc = (
            "The Pradhan Mantri Awas Yojana PMAY was launched in 2015 to provide Housing for All. "
            "It provides financial assistance of 1.20 Lakh to eligible beneficiaries across India."
        )
        self.summary = "PMAY scheme provides financial assistance of 1.20 Lakh for Housing for All."
        self.trans_hi = "पीएम आवास योजना सभी के लिए आवास के लिए 1.20 लाख की वित्तीय सहायता प्रदान करती है।"

    def test_rouge_calculation(self):
        res = NLPAccuracyEvaluator.compute_rouge(self.ref_doc, self.summary)
        self.assertIn("rouge1_f1", res)
        self.assertIn("rouge2_f1", res)
        self.assertIn("rougeL_f1", res)
        self.assertGreater(res["rouge1_f1"], 50.0)
        self.assertGreater(res["rougeL_f1"], 30.0)

    def test_bleu_calculation(self):
        res = NLPAccuracyEvaluator.compute_bleu(self.summary, self.summary)
        self.assertEqual(res["bleu1"], 100.0)

    def test_readability_improvement(self):
        read = NLPAccuracyEvaluator.compute_readability(self.summary)
        self.assertIn("reading_ease", read)
        self.assertGreater(read["reading_ease"], 20.0)

    def test_evaluate_all(self):
        res = NLPAccuracyEvaluator.evaluate_all(self.ref_doc, self.summary, self.trans_hi, target_lang="hi")
        self.assertIn("summarization", res)
        self.assertIn("translation", res)
        self.assertGreater(res["translation"]["adequacy_score"], 80.0)
        self.assertGreater(res["summarization"]["rouge1_f1"], 40.0)


if __name__ == "__main__":
    unittest.main()
