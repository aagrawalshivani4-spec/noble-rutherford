"""
Agentic NLP Framework for Multilingual Government Document Understanding
Full-Stack Flask REST API & Web Server.
Authors: Pallavi, Shivani Agrawal, Vaibhavi K (BMSCE / VTU)
Guide: Prof. Sangeetha S | HOD: Dr. Indiramma M
"""

import os
import io
from flask import Flask, render_template, request, jsonify, send_file, Response
from src.config import SUPPORTED_LANGUAGES, DEFAULT_TARGET_LANGUAGE, SUMMARIZATION_MODELS, DEFAULT_SUMMARIZATION_MODEL
from src.agent.controller import AgenticNLPController
from src.agent.workflow_state import WorkflowExecutionState
from src.qa.rag_engine import DocumentQAEngine
from src.export.exporter import ReportExporter
from src.ingestion.parser import DocumentParser

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload

# Global active workflow state cache for exports and Q&A
_latest_state = None
_latest_qa_engine = None

# Sample Documents mapping
SAMPLE_DOCS = {
    "pmay": "data/sample_documents/pmay_scheme.txt",
    "pm_kisan": "data/sample_documents/pm_kisan_policy.txt",
    "ayushman": "data/sample_documents/ayushman_bharat.txt",
    "nep": "data/sample_documents/nep_2020.txt",
    "pm_kisan_hi": "data/sample_documents/pm_kisan_hindi.txt",
    "gruha_lakshmi_kn": "data/sample_documents/gruha_lakshmi_kannada.txt",
}


@app.route("/")
def index():
    """Renders the main custom HTML5/CSS3 Web Portal."""
    return render_template(
        "index.html",
        languages=SUPPORTED_LANGUAGES,
        default_target=DEFAULT_TARGET_LANGUAGE,
        models=SUMMARIZATION_MODELS
    )


@app.route("/api/sample/<sample_id>", methods=["GET"])
def get_sample(sample_id):
    """Fetches text of pre-packaged government scheme."""
    path = SAMPLE_DOCS.get(sample_id)
    if not path or not os.path.exists(path):
        return jsonify({"error": f"Sample document '{sample_id}' not found."}), 404
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    filename = os.path.basename(path)
    return jsonify({"filename": filename, "text": content})


@app.route("/api/process", methods=["POST"])
def process_document():
    """Main Agentic NLP Workflow execution API."""
    global _latest_state, _latest_qa_engine
    
    document_input = None
    filename = "document.txt"
    target_lang = DEFAULT_TARGET_LANGUAGE
    selected_model = DEFAULT_SUMMARIZATION_MODEL

    if request.is_json:
        data = request.get_json() or {}
        document_input = data.get("text", "")
        filename = data.get("filename", "pasted_text.txt")
        target_lang = data.get("target_language", DEFAULT_TARGET_LANGUAGE)
        selected_model = data.get("model", DEFAULT_SUMMARIZATION_MODEL)
    else:
        target_lang = request.form.get("target_language", DEFAULT_TARGET_LANGUAGE)
        selected_model = request.form.get("model", DEFAULT_SUMMARIZATION_MODEL)
        
        if 'file' in request.files and request.files['file'].filename != '':
            uploaded_file = request.files['file']
            filename = uploaded_file.filename
            file_bytes = uploaded_file.read()
            document_input = file_bytes
        else:
            document_input = request.form.get("text", "")
            filename = request.form.get("filename", "input_text.txt")

    if document_input is None:
        return jsonify({"error": "No document content provided. Please upload a file or paste text."}), 400

    if isinstance(document_input, str) and not document_input.strip():
        return jsonify({"error": "No document content provided. Please upload a file or paste text."}), 400

    if isinstance(document_input, (bytes, bytearray)) and len(document_input) == 0:
        return jsonify({"error": "The uploaded file is empty (0 bytes)."}), 400

    # Ensure selected model is valid
    if selected_model not in SUMMARIZATION_MODELS and selected_model not in SUMMARIZATION_MODELS.values():
        selected_model = DEFAULT_SUMMARIZATION_MODEL

    try:
        # Execute Agentic NLP Pipeline
        controller = AgenticNLPController(summarizer_model=selected_model)
        state = controller.execute_workflow(
            document_input=document_input,
            filename=filename,
            target_language=target_lang
        )

        if state.status == "ERROR":
            return jsonify({"error": f"Workflow failed: {state.error_message}"}), 500

        if not state.raw_text or not state.raw_text.strip():
            return jsonify({
                "error": f"Could not extract readable text from '{filename}'. If this is a scanned PDF image, please provide a PDF with selectable text or paste the text directly."
            }), 400

        _latest_state = state
        _latest_qa_engine = DocumentQAEngine(state.raw_text)

        # Format trace for frontend JSON
        trace_list = []
        for step in state.agent_trace:
            trace_list.append({
                "step_number": step.step_number,
                "step_name": step.step_name,
                "status": step.status,
                "duration_sec": step.duration_sec,
                "description": step.details,
                "metadata": step.metadata
            })

        response_data = {
            "status": state.status,
            "filename": state.document_name,
            "source_language_code": state.source_language_code,
            "source_language_name": state.source_language_name,
            "source_script": state.script_type,
            "target_language_code": state.target_language_code,
            "target_language_name": state.target_language_name,
            "word_count": state.word_count,
            "summary_word_count": state.summary_word_count,
            "compression_ratio": state.compression_ratio,
            "total_latency_sec": state.total_latency_sec,
            "executive_summary": state.executive_summary,
            "bullet_points": state.bullet_points,
            "translated_summary": state.translated_summary,
            "translated_bullet_points": state.translated_bullet_points,
            "extracted_entities": state.extracted_entities,
            "evaluation_metrics": state.evaluation_metrics,
            "agent_trace": trace_list
        }

        return jsonify(response_data)

    except Exception as exc:
        return jsonify({"error": f"Server processing error: {str(exc)}"}), 500


@app.route("/api/qa", methods=["POST"])
def answer_question():
    """Interactive citizen Q&A API grounded in the active document."""
    global _latest_qa_engine, _latest_state
    
    data = request.get_json() or {}
    question = data.get("question", "")

    if not question or not question.strip():
        return jsonify({"error": "Please enter a question."}), 400

    if not _latest_qa_engine:
        if _latest_state and _latest_state.raw_text:
            _latest_qa_engine = DocumentQAEngine(_latest_state.raw_text)
        else:
            return jsonify({"error": "No document has been processed yet. Please process a document first."}), 400

    result = _latest_qa_engine.query(question)
    return jsonify(result)


@app.route("/api/export/json", methods=["GET"])
def export_json():
    """Exports workflow result to formatted JSON download."""
    global _latest_state
    if not _latest_state:
        return jsonify({"error": "No active document state to export."}), 400

    json_str = ReportExporter.to_json(_latest_state)
    return Response(
        json_str,
        mimetype="application/json",
        headers={"Content-Disposition": "attachment;filename=nlp_analysis_report.json"}
    )


@app.route("/api/export/pdf", methods=["GET"])
def export_pdf():
    """Exports workflow result to downloadable PDF report."""
    global _latest_state
    if not _latest_state:
        return jsonify({"error": "No active document state to export."}), 400

    pdf_bytes = ReportExporter.to_pdf_bytes(_latest_state)
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="government_document_analysis_report.pdf"
    )


if __name__ == "__main__":
    print("===================================================================")
    print("🏛️ Agentic NLP Framework - Flask HTML/CSS Web Server")
    print("Department of Artificial Intelligence & Data Science, BMSCE")
    print("Team: Pallavi, Shivani Agrawal, Vaibhavi K")
    print("Server running at: http://127.0.0.1:8080 / http://localhost:8080")
    print("===================================================================")
    app.run(host="0.0.0.0", port=8080, debug=False)
