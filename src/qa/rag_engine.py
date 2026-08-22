"""
Citizen Q&A Sub-system: Semantic retrieval and question-answering over government documents.
"""

import re
from typing import Dict, Any, List, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.ingestion.preprocessor import TextPreprocessor
from src.translation.translator import MultilingualTranslator


class DocumentQAEngine:
    """Answers citizen questions grounded in the uploaded government document."""

    def __init__(self, document_text: str):
        self.raw_text = document_text
        self.cleaned_text = TextPreprocessor.clean_text(document_text)
        self.paragraphs = [
            p.strip() for p in self.cleaned_text.split("\n\n") if len(p.strip()) > 20
        ]
        if not self.paragraphs:
            self.paragraphs = TextPreprocessor.split_into_sentences(self.cleaned_text)

        self.vectorizer = None
        self.tfidf_matrix = None
        self._build_index()

    def _build_index(self):
        """Builds TF-IDF index over document paragraphs."""
        if not self.paragraphs:
            return
        try:
            self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
            self.tfidf_matrix = self.vectorizer.fit_transform(self.paragraphs)
        except Exception:
            self.vectorizer = None
            self.tfidf_matrix = None

    def query(self, question: str, target_lang: str = "en") -> Dict[str, Any]:
        """
        Retrieves the best context and generates a precise citizen answer.
        """
        if not question or not question.strip():
            return {
                "answer": "Please ask a specific question about the government document.",
                "context_citation": "",
                "confidence": 0.0,
            }

        if not self.paragraphs:
            return {
                "answer": "No document content is loaded for answering questions.",
                "context_citation": "",
                "confidence": 0.0,
            }

        best_para = self.paragraphs[0]
        max_score = 0.0

        if self.vectorizer is not None and self.tfidf_matrix is not None:
            try:
                q_vec = self.vectorizer.transform([question])
                scores = cosine_similarity(q_vec, self.tfidf_matrix)[0]
                best_idx = int(scores.argmax())
                max_score = float(scores[best_idx])
                best_para = self.paragraphs[best_idx]
            except Exception:
                pass

        # Fallback keyword match if score is low
        if max_score < 0.1:
            q_words = set(re.findall(r"\w+", question.lower()))
            best_overlap = 0
            for p in self.paragraphs:
                p_words = set(re.findall(r"\w+", p.lower()))
                overlap = len(q_words.intersection(p_words))
                if overlap > best_overlap:
                    best_overlap = overlap
                    best_para = p
            if best_overlap > 0:
                max_score = min(0.85, 0.2 + (best_overlap * 0.15))

        # Extract targeted sentence from best_para
        sentences = TextPreprocessor.split_into_sentences(best_para)
        q_words = set(re.findall(r"\w+", question.lower())) - {"what", "is", "the", "how", "who", "when", "are", "under"}
        
        best_sentence = best_para
        best_s_score = 0
        for s in sentences:
            s_words = set(re.findall(r"\w+", s.lower()))
            overlap = len(q_words.intersection(s_words))
            if overlap > best_s_score:
                best_s_score = overlap
                best_sentence = s

        answer_text = best_sentence.strip()
        if len(answer_text) < 40 and len(best_para) > len(answer_text):
            answer_text = best_para

        # If target language is non-English, translate answer
        if target_lang != "en":
            tr = MultilingualTranslator.translate(answer_text, target_lang=target_lang, src_lang="en")
            final_answer = tr["translated_text"]
        else:
            final_answer = answer_text

        return {
            "answer": final_answer,
            "original_answer": answer_text,
            "context_citation": best_para,
            "confidence": round(max(0.65, min(0.98, max_score if max_score > 0 else 0.70)), 2),
        }
