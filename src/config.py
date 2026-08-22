"""
Configuration and constants for the Agentic NLP Framework.
"""

from typing import Dict, List

# Supported Languages: Focus on 5 Core Indian Regional Languages + English
SUPPORTED_LANGUAGES: Dict[str, Dict[str, str]] = {
    "en": {"name": "English", "native": "English", "script": "Latin", "flag": "🇬🇧"},
    "hi": {"name": "Hindi", "native": "हिन्दी", "script": "Devanagari", "flag": "🇮🇳"},
    "kn": {"name": "Kannada", "native": "ಕನ್ನಡ", "script": "Kannada", "flag": "🇮🇳"},
    "ta": {"name": "Tamil", "native": "தமிழ்", "script": "Tamil", "flag": "🇮🇳"},
    "gu": {"name": "Gujarati", "native": "ગુજરાતી", "script": "Gujarati", "flag": "🇮🇳"},
    "mr": {"name": "Marathi", "native": "मराठी", "script": "Devanagari", "flag": "🇮🇳"},
}

DEFAULT_SOURCE_LANGUAGE = "en"
DEFAULT_TARGET_LANGUAGE = "hi"

# Transformer Model Configurations
SUMMARIZATION_MODELS = {
    "bart-large": "facebook/bart-large-cnn",
    "distilbart": "sshleifer/distilbart-cnn-12-6",
    "flan-t5": "google/flan-t5-small",
    "t5-small": "t5-small",
}

DEFAULT_SUMMARIZATION_MODEL = "distilbart"

# Schema fields for Key Information Extraction
EXTRACTION_SCHEMA_FIELDS = [
    "scheme_name",
    "abbreviation",
    "ministry",
    "objective",
    "target_year",
    "launch_date",
    "benefits",
    "financial_outlay",
    "eligibility_criteria",
    "coverage",
    "required_documents",
    "application_mode",
    "nodal_agency",
    "helpline_or_portal",
]

# Government Document Types
DOCUMENT_TYPES = [
    "Welfare Scheme",
    "National Policy",
    "Administrative Circular",
    "Official Notification",
    "Legislative Act / Bill",
    "Public Notice / Guidelines",
]
