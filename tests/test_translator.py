"""
Unit tests for Multilingual Translation Sub-system.
"""

import unittest
from src.translation.translator import MultilingualTranslator


class TestTranslator(unittest.TestCase):

    def test_same_language_passthrough(self):
        text = "Government welfare scheme"
        res = MultilingualTranslator.translate(text, target_lang="en", src_lang="en")
        self.assertEqual(res["translated_text"], text)

    def test_hindi_translation(self):
        text = "Government of India provides financial assistance"
        res = MultilingualTranslator.translate(text, target_lang="hi", src_lang="en")
        self.assertGreater(len(res["translated_text"]), 5)
        self.assertEqual(res["target_lang"], "hi")

    def test_kannada_translation(self):
        text = "Housing for All"
        res = MultilingualTranslator.translate(text, target_lang="kn", src_lang="en")
        self.assertGreater(len(res["translated_text"]), 3)
        self.assertEqual(res["target_lang"], "kn")


if __name__ == "__main__":
    unittest.main()
