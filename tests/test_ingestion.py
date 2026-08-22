"""
Unit tests for Document Ingestion and Preprocessing modules.
"""

import unittest
from src.ingestion.parser import DocumentParser
from src.ingestion.preprocessor import TextPreprocessor


class TestIngestionAndPreprocessing(unittest.TestCase):

    def test_txt_parser(self):
        sample = "Government of India\n\nMinistry of Education\nNEP 2020 Guidelines"
        res = DocumentParser.parse_txt(sample)
        self.assertEqual(res["format"], "TXT")
        self.assertEqual(res["page_count"], 1)
        self.assertGreater(res["word_count"], 5)
        self.assertIn("NEP 2020", res["raw_text"])

    def test_text_cleaning(self):
        dirty = "  Government   of  India \n\n\n Page 1 of 10 \n\n “Housing for All”  "
        clean = TextPreprocessor.clean_text(dirty)
        self.assertNotIn("Page 1 of 10", clean)
        self.assertIn('"Housing for All"', clean)
        self.assertTrue(clean.startswith("Government of India"))

    def test_sentence_splitting_english_and_indic(self):
        text = "The PM-KISAN scheme was launched in 2019. It provides ₹6,000 per year. यह एक महत्वपूर्ण योजना है।"
        sents = TextPreprocessor.split_into_sentences(text)
        self.assertGreaterEqual(len(sents), 2)

    def test_chunking(self):
        long_text = " ".join([f"Sentence number {i} discusses policy clause {i}." for i in range(100)])
        chunks = TextPreprocessor.chunk_text(long_text, max_chunk_words=50, overlap_words=10)
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(c["word_count"] > 0 for c in chunks))


if __name__ == "__main__":
    unittest.main()
