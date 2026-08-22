"""
Workflow State and Agent Execution Trace Data Structures.
"""

import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class AgentStepLog:
    """Represents a single discrete reasoning or execution step taken by the Agent."""
    step_number: int
    step_name: str
    action: str
    status: str  # "SUCCESS", "RUNNING", "FAILED", "SKIPPED"
    duration_sec: float
    details: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowExecutionState:
    """Holds full state, intermediate outputs, and execution metrics of the Agent."""
    document_name: str = ""
    raw_text: str = ""
    cleaned_text: str = ""
    word_count: int = 0
    page_count: int = 1
    
    # Language Detection
    source_language_code: str = "en"
    source_language_name: str = "English"
    target_language_code: str = "hi"
    target_language_name: str = "Hindi"
    language_confidence: float = 1.0
    script_type: str = "Latin"
    
    # NLP Outputs
    executive_summary: str = ""
    bullet_points: List[str] = field(default_factory=list)
    compression_ratio: str = "0%"
    summary_word_count: int = 0
    summarizer_model: str = ""
    
    # Multilingual Translation
    translated_summary: str = ""
    translated_bullet_points: List[str] = field(default_factory=list)
    translation_backend: str = ""
    
    # Key Information Extraction
    extracted_entities: Dict[str, Any] = field(default_factory=dict)
    
    # Evaluation & Accuracy Metrics
    evaluation_metrics: Dict[str, Any] = field(default_factory=dict)
    
    # Execution Metrics
    start_time: float = 0.0
    end_time: float = 0.0
    total_latency_sec: float = 0.0
    agent_trace: List[AgentStepLog] = field(default_factory=list)
    status: str = "IDLE"  # "IDLE", "PROCESSING", "COMPLETED", "ERROR"
    error_message: Optional[str] = None
