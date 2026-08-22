"""
Unit tests for Language Detection Sub-system.
"""

import unittest
from src.language.detector import LanguageDetector


class TestLanguageDetector(unittest.TestCase):

    def test_detect_english(self):
        text = "The Ministry of Housing and Urban Affairs provides financial subsidies for affordable housing."
        res = LanguageDetector.detect(text)
        self.assertEqual(res["lang_code"], "en")
        self.assertEqual(res["lang_name"], "English")
        self.assertEqual(res["script"], "Latin")
        self.assertGreaterEqual(res["confidence"], 0.8)

    def test_detect_hindi(self):
        text = "प्रधानमंत्री किसान सम्मान निधि योजना भारत सरकार द्वारा किसानों के लिए शुरू की गई है।"
        res = LanguageDetector.detect(text)
        self.assertEqual(res["lang_code"], "hi")
        self.assertEqual(res["lang_name"], "Hindi")
        self.assertEqual(res["script"], "Devanagari")
        self.assertGreaterEqual(res["confidence"], 0.8)

    def test_detect_kannada(self):
        text = "ಕರ್ನಾಟಕ ಸರ್ಕಾರದ ಗೃಹಲಕ್ಷ್ಮಿ ಯೋಜನೆಯು ಮಹಿಳೆಯರಿಗೆ ಮಾಸಿಕ ₹೨,೦೦೦ ನೆರವು ನೀಡುತ್ತದೆ."
        res = LanguageDetector.detect(text)
        self.assertEqual(res["lang_code"], "kn")
        self.assertEqual(res["lang_name"], "Kannada")
        self.assertEqual(res["script"], "Kannada")
        self.assertGreaterEqual(res["confidence"], 0.8)


if __name__ == "__main__":
    unittest.main()
