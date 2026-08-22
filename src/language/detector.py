"""
Language Detection Module: Identifies source language and script distribution
with special support for Indic scripts (Hindi, Kannada, Tamil, Telugu, Marathi, Bengali, Gujarati, Malayalam)
and English.
"""

import re
from typing import Dict, Any, List
from src.config import SUPPORTED_LANGUAGES, DEFAULT_SOURCE_LANGUAGE


class LanguageDetector:
    """Detects document source language, script distribution, and confidence level."""

    SCRIPT_RANGES = {
        "Devanagari": (0x0900, 0x097F),
        "Kannada": (0x0C80, 0x0CFF),
        "Tamil": (0x0B80, 0x0BFF),
        "Telugu": (0x0C00, 0x0C7F),
        "Bengali": (0x0980, 0x09FF),
        "Gujarati": (0x0A80, 0x0AFF),
        "Malayalam": (0x0D00, 0x0D7F),
        "Latin": (0x0041, 0x007A),
    }

    # Distinctive stopwords for Devanagari sub-classification
    MARATHI_MARKERS = {
        "आहे", "आहेत", "आणि", "च्या", "मध्ये", "नाही", "केले", "झाले", "होते", "यांचे",
        "शासनाने", "योजनेचा", "योजनेच्या", "मिळेल", "करणे", "अर्ज", "नोंदणी"
    }
    HINDI_MARKERS = {
        "है", "हैं", "और", "के", "की", "का", "में", "से", "पर", "किया", "गया", "जाएगा",
        "योजना", "सरकार", "दिशानिर्देश", "पात्रता", "लाभार्थी", "वित्तीय", "लाख"
    }

    @classmethod
    def get_script_distribution(cls, text: str) -> Dict[str, float]:
        """Calculates percentage of characters in each Unicode script."""
        if not text:
            return {"Latin": 100.0}

        counts = {script: 0 for script in cls.SCRIPT_RANGES}
        total_letters = 0

        for char in text:
            code = ord(char)
            matched = False
            for script, (start, end) in cls.SCRIPT_RANGES.items():
                if script == "Latin":
                    if ("a" <= char <= "z") or ("A" <= char <= "Z"):
                        counts["Latin"] += 1
                        total_letters += 1
                        matched = True
                        break
                elif start <= code <= end:
                    counts[script] += 1
                    total_letters += 1
                    matched = True
                    break

        if total_letters == 0:
            return {"Latin": 100.0}

        return {
            script: round((cnt / total_letters) * 100.0, 2)
            for script, cnt in counts.items()
            if cnt > 0
        }

    @classmethod
    def detect(cls, text: str) -> Dict[str, Any]:
        """
        Detects the primary language of the text.
        Returns:
            {
                "lang_code": "en" / "hi" / "kn" / etc.,
                "lang_name": "English",
                "native_name": "English",
                "confidence": 0.98,
                "script": "Latin",
                "distribution": {...}
            }
        """
        if not text or not text.strip():
            info = SUPPORTED_LANGUAGES.get(DEFAULT_SOURCE_LANGUAGE, {})
            return {
                "lang_code": DEFAULT_SOURCE_LANGUAGE,
                "lang_name": info.get("name", "English"),
                "native_name": info.get("native", "English"),
                "confidence": 1.0,
                "script": info.get("script", "Latin"),
                "distribution": {"Latin": 100.0},
            }

        distribution = cls.get_script_distribution(text)
        if not distribution:
            primary_script = "Latin"
        else:
            primary_script = max(distribution, key=distribution.get)

        script_to_lang = {
            "Kannada": "kn",
            "Tamil": "ta",
            "Telugu": "te",
            "Bengali": "bn",
            "Gujarati": "gu",
            "Malayalam": "ml",
            "Latin": "en",
        }

        if primary_script == "Devanagari":
            # Disambiguate between Marathi and Hindi
            words = set(re.findall(r"[\u0900-\u097F]+", text.lower()))
            marathi_overlap = len(words.intersection(cls.MARATHI_MARKERS))
            hindi_overlap = len(words.intersection(cls.HINDI_MARKERS))

            if marathi_overlap > hindi_overlap:
                lang_code = "mr"
            else:
                lang_code = "hi"
            confidence = min(0.99, max(0.85, (distribution.get("Devanagari", 80) / 100.0)))
        elif primary_script in script_to_lang:
            lang_code = script_to_lang[primary_script]
            confidence = min(0.99, max(0.85, (distribution.get(primary_script, 80) / 100.0)))
        else:
            lang_code = "en"
            confidence = 0.90

        lang_info = SUPPORTED_LANGUAGES.get(lang_code, SUPPORTED_LANGUAGES["en"])

        return {
            "lang_code": lang_code,
            "lang_name": lang_info["name"],
            "native_name": lang_info["native"],
            "flag": lang_info.get("flag", "🇮🇳"),
            "confidence": round(confidence, 2),
            "script": primary_script,
            "distribution": distribution,
        }
