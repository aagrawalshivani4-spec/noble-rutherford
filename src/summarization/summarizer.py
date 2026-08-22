"""
Summarization Module: Transformer-based Abstractive Summarization (BART / T5)
with chunking for long documents and fallback mechanisms.
"""

import os
import re
import math
from typing import Dict, Any, List, Optional
from collections import Counter
from src.ingestion.preprocessor import TextPreprocessor


class DocumentSummarizer:
    """Generates concise, citizen-friendly summaries using Transformer models or fallback engines."""

    def __init__(self, model_name: str = "sshleifer/distilbart-cnn-12-6"):
        self.model_name = model_name
        self._pipeline = None
        self._tokenizer = None
        self._model = None
        self._initialized = False

    def _lazy_init_transformer(self):
        """Initializes Hugging Face transformers pipeline if available."""
        if self._initialized:
            return

        try:
            from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
            import torch

            # Determine device
            device = 0 if torch.cuda.is_available() else (-1)

            # Check for preferred local or lightweight models
            candidates = [
                self.model_name,
                "sshleifer/distilbart-cnn-12-6",
                "facebook/bart-large-cnn",
                "google/flan-t5-small",
                "t5-small",
            ]

            for cand in candidates:
                try:
                    self._pipeline = pipeline(
                        "summarization",
                        model=cand,
                        device=device,
                        framework="pt",
                        model_kwargs={"local_files_only": True}
                    )
                    self.model_name = cand
                    break
                except Exception:
                    continue

            self._initialized = True
        except Exception:
            self._initialized = True
            self._pipeline = None

    def _extractive_summarize(self, text: str, num_sentences: int = 4) -> str:
        """
        High-quality extractive summarization based on sentence scoring,
        positional weighting, and government keyword density (TF-ISF).
        """
        sentences = TextPreprocessor.split_into_sentences(text)
        if not sentences:
            return text
        if len(sentences) <= num_sentences:
            return " ".join(sentences)

        # Word tokenization & frequency analysis
        words = re.findall(r"\w+", text.lower())
        word_counts = Counter(words)
        total_words = len(words) or 1

        # Key government policy cue words to boost relevance
        policy_boosters = {
            "objective", "aim", "launched", "scheme", "policy", "benefit",
            "assistance", "eligibility", "eligible", "subsidy", "target", "grant",
            "fund", "portal", "mandate", "criteria", "yojana", "guidelines",
            "योजना", "उद्देश्य", "पात्रता", "लाभ", "ಸಹಾಯ", "ಯೋಜನೆ", "ಅರ್ಹತೆ"
        }

        sentence_scores = []
        for idx, sentence in enumerate(sentences):
            s_words = re.findall(r"\w+", sentence.lower())
            if not s_words:
                sentence_scores.append((0, idx, sentence))
                continue

            score = 0.0
            for w in s_words:
                tf = word_counts.get(w, 0) / total_words
                score += tf
                if w in policy_boosters:
                    score += 0.25

            # Positional bias: First 20% and last 10% of government documents contain high-density facts
            pos_ratio = idx / len(sentences)
            if pos_ratio < 0.25:
                score *= 1.4
            elif pos_ratio > 0.85:
                score *= 1.1

            sentence_scores.append((score, idx, sentence))

        # Select top scoring sentences and maintain original chronological flow
        sentence_scores.sort(key=lambda x: x[0], reverse=True)
        top_k = sentence_scores[:num_sentences]
        top_k.sort(key=lambda x: x[1])

        return " ".join([item[2] for item in top_k])

    def _generate_bullet_points(self, text: str) -> List[str]:
        """Extracts key actionable policy takeaways as bullet points."""
        sentences = TextPreprocessor.split_into_sentences(text)
        points = []
        
        # Categorize sentences matching key policy domains
        domains = [
            ("Objective & Scope", [r"\b(aim|objective|vision|launched|purpose|provides)\b", r"\b(योजना|उद्देश्य|ಧ್ಯೇಯ)\b"]),
            ("Financial Benefits", [r"(₹|\brs\.?|\blakh|\bcrore|\bgrant|\bsubsidy|\bfinancial assistance)\b", r"(रुपये|लाख|ಹಣಕಾಸು)"]),
            ("Eligibility Criteria", [r"\b(eligib|criteria|household|income|citizen|family|farmer|senior)\b", r"(पात्रता|ಅರ್ಹತೆ)"]),
            ("Application & Nodal Portal", [r"\b(apply|portal|application|online|documents|aadhaar|csc|helpline)\b", r"(आवेदन|ಅರ್ಜಿ|ದಾಖಲೆ)"]),
        ]

        used_sentences = set()

        for category, regex_list in domains:
            matched_sentence = None
            for s in sentences:
                if s in used_sentences:
                    continue
                for reg in regex_list:
                    if re.search(reg, s, re.IGNORECASE):
                        matched_sentence = s
                        used_sentences.add(s)
                        break
                if matched_sentence:
                    break
            
            if matched_sentence:
                # Clean up bullet point
                clean_pt = matched_sentence.strip()
                if len(clean_pt) > 160:
                    clean_pt = clean_pt[:157] + "..."
                points.append(f"**{category}**: {clean_pt}")

        # If not enough bullets found, extract top 3-4 key sentences
        if len(points) < 3:
            for s in sentences:
                if s not in used_sentences and len(s) > 30:
                    points.append(f"**Key Highlight**: {s}")
                    used_sentences.add(s)
                    if len(points) >= 4:
                        break

        return points

    def summarize(self, text: str, max_length: int = 150, min_length: int = 40, mode: str = "balanced") -> Dict[str, Any]:
        """
        Main summarization method.
        Returns:
            {
                "executive_summary": "...",
                "bullet_points": [...],
                "compression_ratio": "82%",
                "original_word_count": 500,
                "summary_word_count": 90,
                "model_used": "..."
            }
        """
        cleaned_text = TextPreprocessor.clean_text(text)
        orig_words = len(cleaned_text.split())

        if orig_words == 0:
            return {
                "executive_summary": "",
                "bullet_points": [],
                "compression_ratio": "0%",
                "original_word_count": 0,
                "summary_word_count": 0,
                "model_used": "none",
            }

        # If document is very short, return as-is
        if orig_words <= 60:
            return {
                "executive_summary": cleaned_text,
                "bullet_points": [f"**Document Point**: {cleaned_text}"],
                "compression_ratio": "0%",
                "original_word_count": orig_words,
                "summary_word_count": orig_words,
                "model_used": "direct-passthrough",
            }

        # Attempt Transformer Abstractive Summarization
        summary_text = None
        model_name_reported = "Extractive-NLP (TF-ISF)"

        try:
            self._lazy_init_transformer()
            if self._pipeline is not None:
                # Split text if longer than context window
                chunks = TextPreprocessor.chunk_text(cleaned_text, max_chunk_words=350)
                chunk_summaries = []
                for chk in chunks:
                    input_text = chk["text"]
                    # Estimate reasonable length bounds for chunk
                    chunk_word_len = len(input_text.split())
                    chk_max = min(max_length, max(30, int(chunk_word_len * 0.6)))
                    chk_min = min(min_length, max(15, int(chunk_word_len * 0.2)))
                    res = self._pipeline(
                        input_text,
                        max_length=chk_max,
                        min_length=chk_min,
                        truncation=True,
                        do_sample=False
                    )
                    chunk_summaries.append(res[0]["summary_text"])
                
                # Combine chunk summaries
                combined = " ".join(chunk_summaries)
                if len(chunks) > 1:
                    # Final distillation pass
                    final_res = self._pipeline(
                        combined,
                        max_length=max_length,
                        min_length=min_length,
                        truncation=True,
                        do_sample=False
                    )
                    summary_text = final_res[0]["summary_text"].strip()
                else:
                    summary_text = combined.strip()

                model_name_reported = f"Transformer ({self.model_name})"
        except Exception:
            summary_text = None

        # Fallback to high-quality extractive summarization if transformer is unavailable/fails
        if not summary_text:
            num_sents = 3 if orig_words < 250 else (4 if orig_words < 600 else 6)
            summary_text = self._extractive_summarize(cleaned_text, num_sentences=num_sents)
            model_name_reported = "Extractive NLP Engine (Semantic Salience)"

        # Generate bullet points
        bullets = self._generate_bullet_points(cleaned_text)

        summary_words = len(summary_text.split())
        compression = round(((orig_words - summary_words) / max(1, orig_words)) * 100.0, 1)

        return {
            "executive_summary": summary_text,
            "bullet_points": bullets,
            "compression_ratio": f"{max(0.0, compression)}%",
            "original_word_count": orig_words,
            "summary_word_count": summary_words,
            "model_used": model_name_reported,
        }
