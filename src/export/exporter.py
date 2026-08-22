"""
Export Engine: Generates structured downloadable reports in JSON, Markdown, Text,
and PDF formats for government documents and citizen summaries.
"""

import json
import io
from typing import Dict, Any
from src.agent.workflow_state import WorkflowExecutionState


class ReportExporter:
    """Exports processed document results into various downloadable formats."""

    @staticmethod
    def to_json(state: WorkflowExecutionState) -> str:
        """Converts complete workflow state and extracted schema into JSON."""
        data = {
            "metadata": {
                "document_name": state.document_name,
                "word_count": state.word_count,
                "page_count": state.page_count,
                "source_language": state.source_language_name,
                "target_language": state.target_language_name,
                "processing_latency_sec": state.total_latency_sec,
                "status": state.status,
            },
            "summarization": {
                "model": state.summarizer_model,
                "compression_ratio": state.compression_ratio,
                "summary_word_count": state.summary_word_count,
                "executive_summary": state.executive_summary,
                "bullet_points": state.bullet_points,
            },
            "translation": {
                "target_language": state.target_language_name,
                "backend": state.translation_backend,
                "translated_summary": state.translated_summary,
                "translated_bullet_points": state.translated_bullet_points,
            },
            "key_information": state.extracted_entities,
            "agent_execution_trace": [
                {
                    "step": step.step_number,
                    "name": step.step_name,
                    "action": step.action,
                    "status": step.status,
                    "duration_sec": step.duration_sec,
                    "details": step.details,
                }
                for step in state.agent_trace
            ],
        }
        return json.dumps(data, indent=2, ensure_ascii=False)

    @staticmethod
    def to_markdown(state: WorkflowExecutionState) -> str:
        """Converts workflow state into a formatted Markdown report."""
        lines = []
        lines.append(f"# Comprehensive Government Document Understanding Report")
        lines.append(f"**Document Name:** {state.document_name}")
        lines.append(f"**Source Language:** {state.source_language_name} | **Target Language:** {state.target_language_name}")
        lines.append(f"**Processing Time:** {state.total_latency_sec}s | **Compression Ratio:** {state.compression_ratio}")
        lines.append("\n---\n")

        lines.append("## 1. Executive Summary")
        lines.append(state.executive_summary or "No summary generated.")
        lines.append("\n### Key Takeaways")
        for bp in state.bullet_points:
            lines.append(f"- {bp}")

        if state.translated_summary:
            lines.append(f"\n---\n## 2. Regional Translation ({state.target_language_name})")
            lines.append(state.translated_summary)
            if state.translated_bullet_points:
                lines.append(f"\n### {state.target_language_name} Highlights")
                for tbp in state.translated_bullet_points:
                    lines.append(f"- {tbp}")

        if state.extracted_entities:
            lines.append("\n---\n## 3. Extracted Key Information")
            e = state.extracted_entities
            lines.append(f"- **Scheme Name:** {e.get('scheme_name', 'N/A')}")
            lines.append(f"- **Abbreviation:** {e.get('abbreviation', 'N/A')}")
            lines.append(f"- **Sponsoring Ministry:** {e.get('ministry', 'N/A')}")
            lines.append(f"- **Objective:** {e.get('objective', 'N/A')}")
            lines.append(f"- **Target Year / Launch:** {e.get('target_year', 'N/A')}")
            lines.append(f"- **Financial Assistance / Benefits:** {e.get('benefits', 'N/A')}")
            lines.append(f"- **Eligibility Criteria:** {e.get('eligibility_criteria', 'N/A')}")
            lines.append(f"- **Coverage:** {e.get('coverage', 'N/A')}")
            lines.append(f"- **Required Documents:** {', '.join(e.get('required_documents', []))}")
            lines.append(f"- **Official Portal:** {e.get('portal', 'N/A')}")
            lines.append(f"- **Helpline:** {e.get('helpline', 'N/A')}")

        lines.append("\n---\n## 4. Agentic AI Execution Trace")
        for step in state.agent_trace:
            lines.append(f"- **Step {step.step_number} [{step.step_name}]** ({step.duration_sec}s): {step.action}")

        return "\n".join(lines)

    @staticmethod
    def to_pdf_bytes(state: WorkflowExecutionState) -> bytes:
        """
        Generates a standard PDF file of the report.
        """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors

            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
            styles = getSampleStyleSheet()
            story = []

            # Title
            title_style = ParagraphStyle(
                'DocTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor("#1A365D"),
                spaceAfter=12
            )
            story.append(Paragraph("Government Document Understanding Report", title_style))
            story.append(Paragraph(f"<b>Document:</b> {state.document_name} | <b>Latency:</b> {state.total_latency_sec}s", styles['Normal']))
            story.append(Spacer(1, 12))

            # Executive Summary
            story.append(Paragraph("<b>1. Executive Summary</b>", styles['Heading2']))
            story.append(Paragraph(state.executive_summary or "N/A", styles['Normal']))
            story.append(Spacer(1, 10))

            # Key Entities
            if state.extracted_entities:
                story.append(Paragraph("<b>2. Key Extracted Information</b>", styles['Heading2']))
                e = state.extracted_entities
                table_data = [
                    ["Scheme Name", str(e.get("scheme_name", "N/A"))],
                    ["Ministry", str(e.get("ministry", "N/A"))],
                    ["Target Year", str(e.get("target_year", "N/A"))],
                    ["Financial Benefits", str(e.get("benefits", "N/A"))[:120]],
                    ["Coverage", str(e.get("coverage", "N/A"))],
                    ["Official Portal", str(e.get("portal", "N/A"))],
                    ["Helpline", str(e.get("helpline", "N/A"))],
                ]
                t = Table(table_data, colWidths=[130, 380])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
                    ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#2D3748")),
                    ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ]))
                story.append(t)
                story.append(Spacer(1, 12))

            doc.build(story)
            pdf_data = buffer.getvalue()
            buffer.close()
            return pdf_data
        except Exception:
            # Fallback simple text PDF or markdown bytes
            md_text = ReportExporter.to_markdown(state)
            return md_text.encode("utf-8")
