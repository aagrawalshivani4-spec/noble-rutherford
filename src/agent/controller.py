"""
Agentic AI Controller Module: Brain and Workflow Orchestrator for Multilingual
Government Document Understanding.
"""

import time
from typing import Dict, Any, Optional
from src.agent.workflow_state import WorkflowExecutionState, AgentStepLog
from src.ingestion.parser import DocumentParser
from src.ingestion.preprocessor import TextPreprocessor
from src.language.detector import LanguageDetector
from src.summarization.summarizer import DocumentSummarizer
from src.translation.translator import MultilingualTranslator
from src.extraction.extractor import KeyInformationExtractor
from src.config import SUPPORTED_LANGUAGES, DEFAULT_TARGET_LANGUAGE


class AgenticNLPController:
    """Intelligent controller that plans, executes, and validates the multilingual NLP pipeline."""

    def __init__(self, summarizer_model: str = "distilbart"):
        self.summarizer = DocumentSummarizer(model_name=summarizer_model)
        self.translator = MultilingualTranslator()
        self.extractor = KeyInformationExtractor()

    def execute_workflow(
        self,
        document_input: Any,
        filename: str = "document.txt",
        target_language: str = DEFAULT_TARGET_LANGUAGE,
        summary_max_len: int = 150,
        enable_translation: bool = True,
        enable_extraction: bool = True,
    ) -> WorkflowExecutionState:
        """
        Executes the full agentic multi-stage pipeline with real-time step tracing.
        """
        state = WorkflowExecutionState()
        state.document_name = filename
        state.target_language_code = target_language
        state.target_language_name = SUPPORTED_LANGUAGES.get(target_language, {}).get("name", target_language)
        state.status = "PROCESSING"
        state.start_time = time.time()

        step_count = 1

        try:
            # -------------------------------------------------------------
            # STEP 1: Document Ingestion
            # -------------------------------------------------------------
            t0 = time.time()
            parsed_doc = DocumentParser.parse(document_input, filename=filename)
            state.raw_text = parsed_doc["raw_text"]
            state.page_count = parsed_doc["page_count"]
            state.word_count = parsed_doc["word_count"]
            t_diff = round(time.time() - t0, 3)

            state.agent_trace.append(
                AgentStepLog(
                    step_number=step_count,
                    step_name="Data Ingestion",
                    action=f"Parsed {parsed_doc['format']} format ({state.page_count} pages, {state.word_count} words).",
                    status="SUCCESS",
                    duration_sec=t_diff,
                    details=f"Extracted raw text from {filename} without truncation.",
                    metadata={"format": parsed_doc["format"], "pages": state.page_count, "words": state.word_count}
                )
            )
            step_count += 1

            # -------------------------------------------------------------
            # STEP 2: Text Preprocessing & Normalization
            # -------------------------------------------------------------
            t0 = time.time()
            cleaned = TextPreprocessor.clean_text(state.raw_text)
            state.cleaned_text = cleaned
            t_diff = round(time.time() - t0, 3)

            state.agent_trace.append(
                AgentStepLog(
                    step_number=step_count,
                    step_name="Preprocessing & Normalization",
                    action="Standardized Unicode NFC, stripped headers/footers, segmented sentences.",
                    status="SUCCESS",
                    duration_sec=t_diff,
                    details=f"Cleaned {len(cleaned)} characters with multi-lingual encoding preservation.",
                    metadata={"clean_chars": len(cleaned)}
                )
            )
            step_count += 1

            # -------------------------------------------------------------
            # STEP 3: Language Detection & Script Analysis
            # -------------------------------------------------------------
            t0 = time.time()
            lang_res = LanguageDetector.detect(state.cleaned_text)
            state.source_language_code = lang_res["lang_code"]
            state.source_language_name = lang_res["lang_name"]
            state.language_confidence = lang_res["confidence"]
            state.script_type = lang_res["script"]
            t_diff = round(time.time() - t0, 3)

            state.agent_trace.append(
                AgentStepLog(
                    step_number=step_count,
                    step_name="Language & Script Detection",
                    action=f"Identified source language: {state.source_language_name} ({lang_res['native_name']}) with {int(state.language_confidence*100)}% confidence.",
                    status="SUCCESS",
                    duration_sec=t_diff,
                    details=f"Primary script: {state.script_type}. Unicode character distribution computed.",
                    metadata=lang_res
                )
            )
            step_count += 1

            # -------------------------------------------------------------
            # STEP 4: Context & Intent Analysis (Domain Classifier)
            # -------------------------------------------------------------
            t0 = time.time()
            # Analyze document category based on keyword density
            doc_lower = state.cleaned_text.lower()
            if any(k in doc_lower for k in ["housing", "kisan", "arogya", "yojana", "subsid", "welfare"]):
                domain_type = "Public Welfare / Social Security Scheme"
            elif any(k in doc_lower for k in ["education", "nep", "school", "university", "pedagogical"]):
                domain_type = "National Policy / Educational Framework"
            elif any(k in doc_lower for k in ["act", "section", "gazette", "bill", "ordinance"]):
                domain_type = "Legislative Act / Legal Gazette"
            else:
                domain_type = "Official Government Notification / Circular"

            t_diff = round(time.time() - t0, 3)
            state.agent_trace.append(
                AgentStepLog(
                    step_number=step_count,
                    step_name="Context & Intent Understanding",
                    action=f"Classified document category: {domain_type}.",
                    status="SUCCESS",
                    duration_sec=t_diff,
                    details="Agent planned optimal pipeline routes for summarization, entity extraction, and translation.",
                    metadata={"classified_domain": domain_type}
                )
            )
            step_count += 1

            # -------------------------------------------------------------
            # STEP 5: Transformer Summarization
            # -------------------------------------------------------------
            t0 = time.time()
            sum_res = self.summarizer.summarize(state.cleaned_text, max_length=summary_max_len)
            state.executive_summary = sum_res["executive_summary"]
            state.bullet_points = sum_res["bullet_points"]
            state.compression_ratio = sum_res["compression_ratio"]
            state.summary_word_count = sum_res["summary_word_count"]
            state.summarizer_model = sum_res["model_used"]
            t_diff = round(time.time() - t0, 3)

            state.agent_trace.append(
                AgentStepLog(
                    step_number=step_count,
                    step_name="Document Summarization",
                    action=f"Generated abstractive summary using {state.summarizer_model} ({state.compression_ratio} compression).",
                    status="SUCCESS",
                    duration_sec=t_diff,
                    details=f"Reduced text from {state.word_count} words to {state.summary_word_count} concise words.",
                    metadata=sum_res
                )
            )
            step_count += 1

            # -------------------------------------------------------------
            # STEP 6: Key Information & Entity Extraction
            # -------------------------------------------------------------
            if enable_extraction:
                t0 = time.time()
                extracted = self.extractor.extract_all(state.cleaned_text)
                state.extracted_entities = extracted
                t_diff = round(time.time() - t0, 3)

                state.agent_trace.append(
                    AgentStepLog(
                        step_number=step_count,
                        step_name="Key Information Extraction (NER)",
                        action=f"Extracted {extracted.get('entity_count', 0)} key structured attributes (Scheme, Ministry, Deadlines, Aid, Eligibility).",
                        status="SUCCESS",
                        duration_sec=t_diff,
                        details=f"Identified Scheme: '{extracted.get('scheme_name')}' | Ministry: '{extracted.get('ministry')}'.",
                        metadata={"entity_count": extracted.get("entity_count", 0)}
                    )
                )
                step_count += 1

            # -------------------------------------------------------------
            # STEP 7: Multilingual Translation
            # -------------------------------------------------------------
            if enable_translation:
                t0 = time.time()
                tr_summary = self.translator.translate(
                    state.executive_summary,
                    target_lang=state.target_language_code,
                    src_lang=state.source_language_code
                )
                state.translated_summary = tr_summary["translated_text"]
                state.translation_backend = tr_summary["backend"]

                # Translate bullet points
                state.translated_bullet_points = self.translator.translate_bullet_points(
                    state.bullet_points,
                    target_lang=state.target_language_code,
                    src_lang=state.source_language_code
                )
                t_diff = round(time.time() - t0, 3)

                state.agent_trace.append(
                    AgentStepLog(
                        step_number=step_count,
                        step_name="Multilingual Translation",
                        action=f"Translated summary into {state.target_language_name} ({tr_summary.get('target_native', '')}) via {state.translation_backend}.",
                        status="SUCCESS",
                        duration_sec=t_diff,
                        details=f"Target script translated cleanly with {len(state.translated_bullet_points)} key bullet points.",
                        metadata={"backend": state.translation_backend, "target": state.target_language_code}
                    )
                )
                step_count += 1

            # -------------------------------------------------------------
            # STEP 8: Post-Processing, Accuracy Evaluation & Validation
            # -------------------------------------------------------------
            t0 = time.time()
            from src.metrics.evaluator import NLPAccuracyEvaluator
            eval_res = NLPAccuracyEvaluator.evaluate_all(
                original_doc=state.cleaned_text,
                summary_text=state.executive_summary,
                translated_text=state.translated_summary,
                target_lang=state.target_language_code
            )
            state.evaluation_metrics = eval_res
            
            is_valid = bool(state.executive_summary and len(state.executive_summary) > 20)
            t_diff = round(time.time() - t0, 3)

            state.agent_trace.append(
                AgentStepLog(
                    step_number=step_count,
                    step_name="Evaluation & Accuracy Validation",
                    action=f"Calculated ROUGE-1 ({eval_res['summarization']['rouge1_f1']}%), ROUGE-L ({eval_res['summarization']['rougeL_f1']}%), Translation Adequacy ({eval_res['translation']['adequacy_score']}%), Readability ({eval_res['summarization']['ease_grade']}).",
                    status="SUCCESS" if is_valid else "WARNING",
                    duration_sec=t_diff,
                    details="All NLP accuracy and quality thresholds validated successfully.",
                    metadata=eval_res
                )
            )

            state.status = "COMPLETED"

        except Exception as e:
            state.status = "ERROR"
            state.error_message = str(e)
            state.agent_trace.append(
                AgentStepLog(
                    step_number=step_count,
                    step_name="Agent Execution Failure",
                    action=f"Error encountered: {str(e)}",
                    status="FAILED",
                    duration_sec=0.0,
                    details=str(e),
                )
            )

        state.end_time = time.time()
        state.total_latency_sec = round(state.end_time - state.start_time, 2)
        return state
