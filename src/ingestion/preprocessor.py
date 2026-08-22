"""
Document Preprocessing Module: Text cleaning, Unicode normalization,
sentence segmentation, and semantic chunking.
"""

import re
import unicodedata
from typing import List, Dict, Any


class TextPreprocessor:
    """Cleans and prepares government document text for NLP processing."""

    @staticmethod
    def normalize_unicode(text: str) -> str:
        """Normalizes unicode text, ensuring correct rendering of Indic scripts."""
        if not text:
            return ""
        # NFC is canonical decomposition followed by canonical composition
        return unicodedata.normalize("NFC", text)

    @staticmethod
    def clean_text(text: str) -> str:
        """Removes excessive whitespace, header/footer noise, and artifacts."""
        if not text:
            return ""

        # Normalize unicode
        text = unicodedata.normalize("NFC", text)

        # Replace non-breaking spaces and special zero-width characters
        text = text.replace("\u200b", "").replace("\ufeff", "").replace("\xa0", " ")

        # Normalize quotation marks and dashes
        text = text.replace("\u201c", '"').replace("\u201d", '"').replace("\u201e", '"').replace("\u201f", '"')
        text = text.replace("\u2018", "'").replace("\u2019", "'").replace("\u201a", "'").replace("\u201b", "'")
        text = text.replace("\u2013", "-").replace("\u2014", "-").replace("\u2015", "-")

        # Remove repetitive header/footer page patterns like "Page 1 of 10" or "Page 1"
        text = re.sub(r"(?i)page\s+\d+\s+of\s+\d+", "", text)
        text = re.sub(r"(?i)page\s+\d+", "", text)

        # Remove excessive repeated blank lines and horizontal rules
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n\s*\n+", "\n\n", text)

        return text.strip()

    @classmethod
    def split_into_sentences(cls, text: str) -> List[str]:
        """Splits text into sentences supporting English and Indian sentence terminators."""
        text = cls.clean_text(text)
        if not text:
            return []

        # Split on '.', '!', '?', or Indic purna viram '।' / double purna viram '॥'
        # with lookbehind/lookahead to avoid splitting on decimals like 2.5 or ₹1.20
        pattern = r"(?<=[.!?।॥])\s+(?=[A-Z0-9\u0900-\u0D7F])|\n\n+"
        raw_sentences = re.split(pattern, text)

        sentences = []
        for s in raw_sentences:
            cleaned = s.strip()
            if len(cleaned) > 5:
                sentences.append(cleaned)
        return sentences

    @classmethod
    def chunk_text(cls, text: str, max_chunk_words: int = 400, overlap_words: int = 50) -> List[Dict[str, Any]]:
        """
        Splits lengthy government documents into semantic chunks with overlap
        for transformer context window processing.
        """
        text = cls.clean_text(text)
        sentences = cls.split_into_sentences(text)

        chunks = []
        current_chunk = []
        current_word_count = 0

        for sentence in sentences:
            sentence_words = len(sentence.split())
            if current_word_count + sentence_words > max_chunk_words and current_chunk:
                chunk_text = " ".join(current_chunk)
                chunks.append({
                    "chunk_id": len(chunks) + 1,
                    "text": chunk_text,
                    "word_count": len(chunk_text.split()),
                    "sentence_count": len(current_chunk),
                })
                # Retain overlap sentences if possible
                overlap_sentences = []
                overlap_count = 0
                for s in reversed(current_chunk):
                    s_count = len(s.split())
                    if overlap_count + s_count <= overlap_words:
                        overlap_sentences.insert(0, s)
                        overlap_count += s_count
                    else:
                        break
                current_chunk = list(overlap_sentences)
                current_word_count = overlap_count

            current_chunk.append(sentence)
            current_word_count += sentence_words

        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append({
                "chunk_id": len(chunks) + 1,
                "text": chunk_text,
                "word_count": len(chunk_text.split()),
                "sentence_count": len(current_chunk),
            })

        return chunks
