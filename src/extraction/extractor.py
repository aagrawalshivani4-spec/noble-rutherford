"""
Key Information Extraction Module: Extracts structured metadata, schemes,
financial assistance, eligibility criteria, target years, and entities from
government documents.
"""

import re
from typing import Dict, Any, List, Optional
from src.ingestion.preprocessor import TextPreprocessor


class KeyInformationExtractor:
    """Extracts structured government scheme/policy information and named entities."""

    # Pre-defined known government scheme patterns and entities
    SCHEME_PATTERNS = [
        r"(Pradhan Mantri [A-Za-z\s]+ Yojana|PM-[A-Z]+|PMAY(?:-[UG])?|PM-KISAN|PM-JAY|AB-PMJAY|NIPUN Bharat|Digital India|National Education Policy \d{4}|NEP \d{4}|Gruha Lakshmi(?: Scheme)?|Swachh Bharat Mission|MGNREGS)",
        r"(प्रधानमंत्री [^\n,]+ योजना|पीएम-[^\n,]+|ಗೃಹಲಕ್ಷ್ಮಿ ಯೋಜನೆ|ರಾಷ್ಟ್ರೀಯ ಶಿಕ್ಷಣ ನೀತಿ)",
    ]

    MINISTRY_PATTERNS = [
        r"(Ministry of [A-Za-z\s&,]+(?:Affairs|Development|Welfare|Health|Education|Finance|Agriculture|Electronics))",
        r"(Department of [A-Za-z\s&,]+(?:Affairs|Development|Welfare|Education|Agriculture))",
        r"(National Health Authority|NITI Aayog|University Grants Commission|Reserve Bank of India)",
        r"(ಕರ್ನಾಟಕ ಸರ್ಕಾರ|ಮಹಿಳಾ ಮತ್ತು ಮಕ್ಕಳ ಅಭಿವೃದ್ಧಿ ಇಲಾಖೆ|ಭಾರತ ಸರ್ಕಾರ)",
        r"(भारत सरकार|कृषि एवं किसान कल्याण मंत्रालय|आवासन और शहरी कार्य मंत्रालय|राष्ट्रीय स्वास्थ्य प्राधिकरण)",
    ]

    YEAR_PATTERNS = [
        r"\b(?:target year|by|year)\s*[:\-]?\s*(20\d\d)\b",
        r"\b(?:launched in|approved on|dated)\s*[:\-]?\s*([0-9]{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+\s+20\d\d|20\d\d)\b",
        r"\b(202[4-9]|203[0-5])\b",
    ]

    FINANCIAL_PATTERNS = [
        r"(₹\s*[\d,]+(?:\.\d+)?\s*(?:Lakh|Crore|per annum|per family|per unit|per month)?|Rs\.?\s*[\d,]+(?:\.\d+)?\s*(?:Lakh|Crore)?)",
        r"(₹[೦-೯,]+|ರೂ\.?\s*[೦-೯,]+)",
        r"(₹\s*[०-९,]+(?:\s*लाख|\s*करोड़)?)",
        r"(?:financial assistance|grant|subsidy|health cover|benefit) of\s+([^,.;\n]+)",
    ]

    COVERAGE_PATTERNS = [
        r"(Urban and Rural Areas|All-India|Nationwide|Pan-India|Urban Areas|Rural Districts|All 4,372 statutory towns|Karnataka|All States and UTs)",
        r"(शहरी और ग्रामीण|ಸಮಗ್ರ ಕರ್ನಾಟಕ|ಎಲ್ಲಾ ಜಿಲ್ಲೆಗಳು)",
    ]

    @classmethod
    def extract_scheme_name(cls, text: str) -> Dict[str, str]:
        """Extracts scheme or policy title and abbreviation."""
        # Check explicit title patterns
        for pattern in cls.SCHEME_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                full_name = match.group(0).strip()
                # Check for abbreviation inside parentheses or standalone
                abbr_match = re.search(r"\(([A-Z0-9\-]+)\)", text)
                abbr = abbr_match.group(1) if abbr_match else ""
                if not abbr:
                    # Look for known short acronyms in the name
                    acronyms = re.findall(r"\b([A-Z]{3,}(?:-[A-Z]+)?)\b", full_name)
                    abbr = acronyms[0] if acronyms else ""
                return {"name": full_name, "abbreviation": abbr}

        # Fallback: inspect top lines of document
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        for line in lines[:5]:
            if any(k in line.lower() for k in ["scheme", "policy", "yojana", "guidelines", "act", "mission"]):
                return {"name": line, "abbreviation": ""}

        return {"name": "Government Public Policy / Scheme", "abbreviation": "GOV-DOC"}

    @classmethod
    def extract_ministry(cls, text: str) -> str:
        """Extracts governing ministry or department."""
        for pattern in cls.MINISTRY_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()

        # Check line headers
        for line in text.split("\n")[:8]:
            if "ministry" in line.lower() or "department" in line.lower() or "authority" in line.lower() or "ಸರ್ಕಾರ" in line or "मंत्रालय" in line:
                return line.strip()

        return "Government of India / State Authority"

    @classmethod
    def extract_objective(cls, text: str) -> str:
        """Extracts primary purpose or objective statement."""
        sentences = TextPreprocessor.split_into_sentences(text)
        for s in sentences:
            if re.search(r"\b(objective|aims? to|vision|purpose of the scheme|launched with the)\b", s, re.IGNORECASE):
                # Clean up heading if attached
                cleaned = re.sub(r"^[0-9.\s]+(SCHEME OVERVIEW AND OBJECTIVE|OBJECTIVE|PURPOSE)[:\-]?\s*", "", s, flags=re.IGNORECASE)
                return cleaned.strip()
            if re.search(r"(उद्देश्य|ಧ್ಯೇಯ|ಉದ್ದೇಶ)", s):
                return s.strip()

        # Fallback to first major descriptive sentence
        for s in sentences[:3]:
            if len(s) > 40:
                return s.strip()

        return "Facilitate public welfare, financial assistance, and citizen empowerment."

    @classmethod
    def extract_target_year(cls, text: str) -> str:
        """Extracts target completion year or launch date."""
        # Search for deadline / target year
        target_match = re.search(r"(?:target year|by the year|by)\s*[:\-]?\s*(20\d\d)", text, re.IGNORECASE)
        if target_match:
            return target_match.group(1)

        # Search for launch date
        launch_match = re.search(r"(?:launched in|launched on|effective from)\s*([A-Za-z0-9,\s]+?20\d\d)", text, re.IGNORECASE)
        if launch_match:
            return launch_match.group(1).strip()

        # Search generic year
        years = re.findall(r"\b(202[0-9]|203[0-5])\b", text)
        if years:
            return years[-1]

        return "Ongoing / 2025-2026"

    @classmethod
    def extract_benefits(cls, text: str) -> str:
        """Extracts financial benefits, subsidies, or healthcare cover."""
        sentences = TextPreprocessor.split_into_sentences(text)
        benefit_sentences = []
        for s in sentences:
            if re.search(r"\b(financial assistance|subsidy|health cover|₹|rs\.?|dbt|grant|per annum|per family|installment)\b", s, re.IGNORECASE) or re.search(r"(रुपये|लाख|ಹಣಕಾಸು|ನೆರವು)", s):
                # Remove section numbers
                cleaned = re.sub(r"^[0-9.\s\-\*]+", "", s).strip()
                if cleaned and cleaned not in benefit_sentences:
                    benefit_sentences.append(cleaned)
                if len(benefit_sentences) >= 2:
                    break

        if benefit_sentences:
            return " | ".join(benefit_sentences)

        # Fallback to regex amounts
        amounts = re.findall(r"(₹\s*[\d,]+(?:\.\d+)?\s*(?:Lakh|Crore|per annum|per month)?)", text, re.IGNORECASE)
        if amounts:
            return f"Financial support including {', '.join(amounts[:3])}"

        return "Direct financial assistance and subsidized welfare support."

    @classmethod
    def extract_eligibility(cls, text: str) -> str:
        """Extracts eligibility criteria and household conditions."""
        sentences = TextPreprocessor.split_into_sentences(text)
        elig_sentences = []
        for s in sentences:
            if re.search(r"\b(eligib|household|income|bpl|ews|lig|farmer|landholding|citizen|beneficiary)\b", s, re.IGNORECASE) or re.search(r"(पात्रता|ಅರ್ಹತೆ)", s):
                cleaned = re.sub(r"^[0-9.\s\-\*]+", "", s).strip()
                if cleaned and len(cleaned) > 20:
                    elig_sentences.append(cleaned)
                if len(elig_sentences) >= 2:
                    break

        if elig_sentences:
            return " ".join(elig_sentences)

        return "All eligible citizens and households meeting the scheme criteria."

    @classmethod
    def extract_coverage(cls, text: str) -> str:
        """Extracts geographic coverage scope."""
        for pattern in cls.COVERAGE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()

        if "urban" in text.lower() and "rural" in text.lower():
            return "Urban and Rural Areas (Nationwide)"
        elif "urban" in text.lower():
            return "Urban Statutory Towns"
        elif "rural" in text.lower():
            return "Rural Districts Pan-India"

        return "National / State-wide Coverage"

    @classmethod
    def extract_documents_required(cls, text: str) -> List[str]:
        """Extracts list of required identification and financial documents."""
        docs = []
        doc_keywords = [
            ("Aadhaar Card", r"\b(aadhaar|aadhar|uid)\b"),
            ("Income Certificate / BPL Card", r"\b(income certificate|bpl card|ration card|salary slip)\b"),
            ("Bank Account / Passbook (Aadhaar linked)", r"\b(bank account|passbook|ifsc|dbt)\b"),
            ("Land Record / RTC / Khatauni", r"\b(land record|khasra|khatauni|rtc|ror|title deed)\b"),
            ("Address / Residence Proof", r"\b(address proof|voter id|electricity bill)\b"),
            ("Self-Declaration Affidavit", r"\b(affidavit|declaration)\b"),
        ]

        for name, pattern in doc_keywords:
            if re.search(pattern, text, re.IGNORECASE) or re.search(pattern, text):
                docs.append(name)

        if not docs:
            docs = ["Aadhaar Card", "Bank Account Details", "Income/Identity Proof"]

        return docs

    @classmethod
    def extract_portal_and_helpline(cls, text: str) -> Dict[str, str]:
        """Extracts official portal URL and helpline contact number."""
        # Find URLs
        url_match = re.search(r"https?://[^\s,\)\]]+", text)
        portal = url_match.group(0) if url_match else "Official Government Portal"

        # Find Phone / Toll-free numbers
        phone_match = re.search(r"(?:helpline|toll-free|call|phone|number)?\s*[:\-]?\s*(\b1[0-9]{3,4}\b|\b1800[-\s]?[0-9]{3}[-\s]?[0-9]{3,4}\b|\b011-[0-9]{8}\b|\b080-[0-9]{8}\b)", text, re.IGNORECASE)
        helpline = phone_match.group(1) if phone_match else "1800-11-6163 / 14555"

        return {"portal": portal, "helpline": helpline}

    @classmethod
    def extract_all(cls, text: str) -> Dict[str, Any]:
        """
        Runs comprehensive key information extraction.
        Returns a structured dictionary adhering to the system schema.
        """
        scheme_info = cls.extract_scheme_name(text)
        ministry = cls.extract_ministry(text)
        objective = cls.extract_objective(text)
        target_year = cls.extract_target_year(text)
        benefits = cls.extract_benefits(text)
        eligibility = cls.extract_eligibility(text)
        coverage = cls.extract_coverage(text)
        required_docs = cls.extract_documents_required(text)
        contacts = cls.extract_portal_and_helpline(text)

        # Count total entities found for analytics
        entity_count = sum([
            1 if scheme_info["name"] else 0,
            1 if scheme_info["abbreviation"] else 0,
            1 if ministry else 0,
            1 if target_year else 0,
            1 if benefits else 0,
            1 if eligibility else 0,
            1 if coverage else 0,
            len(required_docs),
            1 if contacts["portal"] else 0,
            1 if contacts["helpline"] else 0,
        ])

        return {
            "scheme_name": scheme_info["name"],
            "abbreviation": scheme_info["abbreviation"] or "N/A",
            "ministry": ministry,
            "objective": objective,
            "target_year": target_year,
            "benefits": benefits,
            "eligibility_criteria": eligibility,
            "coverage": coverage,
            "required_documents": required_docs,
            "portal": contacts["portal"],
            "helpline": contacts["helpline"],
            "entity_count": entity_count,
        }
