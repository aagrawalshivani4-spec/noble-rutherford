"""
Agentic NLP Framework for Multilingual Government Document Understanding
Main Streamlit Application Entrypoint
Authors: Pallavi, Shivani Agrawal, Vaibhavi K (BMSCE / VTU)
"""

import os
import streamlit as st
from src.config import SUPPORTED_LANGUAGES, DEFAULT_TARGET_LANGUAGE, SUMMARIZATION_MODELS
from src.agent.controller import AgenticNLPController
from src.agent.workflow_state import WorkflowExecutionState
from src.language.detector import LanguageDetector
from src.qa.rag_engine import DocumentQAEngine
from src.export.exporter import ReportExporter
from src.ui.styles import CUSTOM_CSS
from src.ui.components import (
    render_header,
    render_kpi_metrics,
    render_agent_trace,
    render_key_information_card,
    render_analytics_charts,
    render_accuracy_metrics_view,
)

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Agentic NLP Framework - Multilingual Government Documents",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply Custom CSS styling
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def init_session_state():
    """Initializes session state variables for state persistence across interactions."""
    if "workflow_state" not in st.session_state:
        st.session_state.workflow_state = None
    if "qa_engine" not in st.session_state:
        st.session_state.qa_engine = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "current_doc_text" not in st.session_state:
        st.session_state.current_doc_text = ""
    if "doc_filename" not in st.session_state:
        st.session_state.doc_filename = ""


init_session_state()


def load_sample_document(sample_name: str) -> str:
    """Loads a pre-packaged sample government document from data directory."""
    path_map = {
        "PMAY - Pradhan Mantri Awas Yojana": "data/sample_documents/pmay_scheme.txt",
        "PM-KISAN - Farmer Income Support Scheme": "data/sample_documents/pm_kisan_policy.txt",
        "Ayushman Bharat - PM-JAY Healthcare": "data/sample_documents/ayushman_bharat.txt",
        "NEP 2020 - National Education Policy": "data/sample_documents/nep_2020.txt",
        "PM-KISAN (Hindi Document)": "data/sample_documents/pm_kisan_hindi.txt",
        "Gruha Lakshmi Scheme (Kannada Document)": "data/sample_documents/gruha_lakshmi_kannada.txt",
    }
    file_path = path_map.get(sample_name)
    if file_path and os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


# -------------------------------------------------------------
# SIDEBAR CONTROLS
# -------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/government.png", width=56)
    st.title("Framework Controls")
    st.caption("🏛️ Major Project • Dept. of AI & DS, BMSCE")

    st.markdown("---")
    st.subheader("⚙️ NLP Model Settings")
    model_choice = st.selectbox(
        "Summarization Model",
        options=list(SUMMARIZATION_MODELS.keys()),
        index=1,
        help="Select transformer summarization backbone (BART / DistilBART / T5)",
    )

    st.subheader("🌐 Target Translation")
    target_lang_code = st.selectbox(
        "Preferred Regional Language",
        options=list(SUPPORTED_LANGUAGES.keys()),
        format_func=lambda x: f"{SUPPORTED_LANGUAGES[x]['flag']} {SUPPORTED_LANGUAGES[x]['name']} ({SUPPORTED_LANGUAGES[x]['native']})",
        index=list(SUPPORTED_LANGUAGES.keys()).index(DEFAULT_TARGET_LANGUAGE),
    )

    st.markdown("---")
    st.subheader("📂 Sample Government Documents")
    sample_selection = st.selectbox(
        "Load Pre-packaged Document",
        options=[
            "-- Select a Sample Document --",
            "PMAY - Pradhan Mantri Awas Yojana",
            "PM-KISAN - Farmer Income Support Scheme",
            "Ayushman Bharat - PM-JAY Healthcare",
            "NEP 2020 - National Education Policy",
            "PM-KISAN (Hindi Document)",
            "Gruha Lakshmi Scheme (Kannada Document)",
        ],
    )

    if sample_selection != "-- Select a Sample Document --":
        if st.button("📥 Load Sample into Input"):
            loaded_text = load_sample_document(sample_selection)
            if loaded_text:
                st.session_state.current_doc_text = loaded_text
                st.session_state.doc_filename = f"{sample_selection.split(' - ')[0].replace(' ', '_').lower()}.txt"
                st.success(f"Loaded {sample_selection}")

    st.markdown("---")
    st.markdown(
        """
        <div class="sidebar-team-box">
            <div class="sidebar-team-title">👥 Project Team</div>
            <div class="team-member">1. Pallavi <span class="team-usn">(1BM23AD041)</span></div>
            <div class="team-member">2. Shivani Agrawal <span class="team-usn">(1BM23AD058)</span></div>
            <div class="team-member">3. Vaibhavi K <span class="team-usn">(1BM22AD065)</span></div>
            <hr style="margin: 0.6rem 0; border: 0; border-top: 1px solid #E2E8F0;"/>
            <div style="font-size: 0.8rem; color: #475569;">
                <b>Guide:</b> Prof. Sangeetha S<br/>
                <b>HOD:</b> Dr. Indiramma M<br/>
                <i>BMS College of Engineering, Bengaluru</i>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -------------------------------------------------------------
# MAIN APPLICATION BODY
# -------------------------------------------------------------
render_header()

# Quick Reset Button on Top Right
col_head_l, col_head_r = st.columns([5, 1])
with col_head_r:
    if st.button("🔄 Reset All", use_container_width=True):
        st.session_state.workflow_state = None
        st.session_state.qa_engine = None
        st.session_state.chat_history = []
        st.session_state.current_doc_text = ""
        st.session_state.doc_filename = ""
        st.rerun()

# -------------------------------------------------------------
# 1. DOCUMENT UPLOAD & INPUT AREA
# -------------------------------------------------------------
st.markdown("### 1. Select or Upload Government Document")

# Quick 1-Click Sample Schemes directly on the main screen
st.markdown("**⚡ 1-Click Pre-loaded Government Documents (Click any to load instantly):**")
row1_c1, row1_c2, row1_c3 = st.columns(3)
with row1_c1:
    if st.button("🏠 PMAY (Housing Scheme)", use_container_width=True):
        st.session_state.current_doc_text = load_sample_document("PMAY - Pradhan Mantri Awas Yojana")
        st.session_state.doc_filename = "pmay_scheme.txt"
        st.rerun()
with row1_c2:
    if st.button("🌾 PM-KISAN (Farmer Scheme)", use_container_width=True):
        st.session_state.current_doc_text = load_sample_document("PM-KISAN - Farmer Income Support Scheme")
        st.session_state.doc_filename = "pm_kisan_policy.txt"
        st.rerun()
with row1_c3:
    if st.button("🏥 Ayushman Bharat (Health)", use_container_width=True):
        st.session_state.current_doc_text = load_sample_document("Ayushman Bharat - PM-JAY Healthcare")
        st.session_state.doc_filename = "ayushman_bharat.txt"
        st.rerun()

row2_c1, row2_c2, row2_c3 = st.columns(3)
with row2_c1:
    if st.button("🎓 NEP 2020 (Education)", use_container_width=True):
        st.session_state.current_doc_text = load_sample_document("NEP 2020 - National Education Policy")
        st.session_state.doc_filename = "nep_2020.txt"
        st.rerun()
with row2_c2:
    if st.button("🇮🇳 PM-KISAN (Hindi Text)", use_container_width=True):
        st.session_state.current_doc_text = load_sample_document("PM-KISAN (Hindi Document)")
        st.session_state.doc_filename = "pm_kisan_hindi.txt"
        st.rerun()
with row2_c3:
    if st.button("🟡 Gruha Lakshmi (Kannada)", use_container_width=True):
        st.session_state.current_doc_text = load_sample_document("Gruha Lakshmi Scheme (Kannada Document)")
        st.session_state.doc_filename = "gruha_lakshmi_kannada.txt"
        st.rerun()

st.markdown("---")

# Auto-default to PMAY if nothing is selected yet so screen is never empty
if not st.session_state.current_doc_text:
    st.session_state.current_doc_text = load_sample_document("PMAY - Pradhan Mantri Awas Yojana")
    st.session_state.doc_filename = "pmay_scheme.txt"

tab_sample, tab_upload, tab_paste = st.tabs(["📄 Active Document Preview", "📤 Upload Your Own File (PDF / TXT)", "✍️ Paste Custom Text"])

with tab_sample:
    st.markdown(f"**Loaded Document:** `{st.session_state.doc_filename or 'pmay_scheme.txt'}`")
    preview_txt = st.session_state.current_doc_text if isinstance(st.session_state.current_doc_text, str) else "[Binary PDF Content Loaded]"
    st.text_area("Document Content Preview:", value=preview_txt, height=160, disabled=True)

with tab_upload:
    uploaded_file = st.file_uploader(
        "Upload any Government PDF or TXT document from your computer",
        type=["pdf", "txt"],
        help="Supported formats: Digital PDF, Plain Text (UTF-8)",
    )
    if uploaded_file is not None:
        st.session_state.doc_filename = uploaded_file.name
        if uploaded_file.name.lower().endswith(".pdf"):
            st.session_state.current_doc_text = uploaded_file.getvalue()
        else:
            try:
                st.session_state.current_doc_text = uploaded_file.getvalue().decode("utf-8")
            except Exception:
                st.session_state.current_doc_text = uploaded_file.getvalue().decode("latin-1")

with tab_paste:
    pasted = st.text_area(
        "Or paste custom government text here:",
        value=st.session_state.current_doc_text if isinstance(st.session_state.current_doc_text, str) else "",
        height=160,
        placeholder="Paste government circular or policy text here...",
    )
    if pasted.strip() and pasted != preview_txt:
        st.session_state.current_doc_text = pasted
        st.session_state.doc_filename = "custom_document.txt"

# -------------------------------------------------------------
# LANGUAGE DETECTION PREVIEW & ACTION
# -------------------------------------------------------------
if st.session_state.current_doc_text:
    # Quick preview of detected language
    preview_sample = st.session_state.current_doc_text if isinstance(st.session_state.current_doc_text, str) else "PDF Document"
    lang_info = LanguageDetector.detect(preview_sample[:1000])

    col_det, col_tgt, col_act = st.columns([2, 2, 2])
    with col_det:
        st.markdown(
            f"""
            <div style="background: #F1F5F9; padding: 0.6rem 1rem; border-radius: 8px; border: 1px solid #CBD5E1;">
                <span style="font-size: 0.75rem; color: #64748B; font-weight: 600;">DETECTED SOURCE LANGUAGE</span><br/>
                <span style="font-size: 1.05rem; font-weight: 700; color: #1E293B;">{lang_info['flag']} {lang_info['lang_name']} ({lang_info['native_name']})</span>
                <span style="font-size: 0.75rem; color: #10B981; margin-left: 5px;">• {int(lang_info['confidence']*100)}% Match</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_tgt:
        tgt_info = SUPPORTED_LANGUAGES.get(target_lang_code, {})
        st.markdown(
            f"""
            <div style="background: #EFF6FF; padding: 0.6rem 1rem; border-radius: 8px; border: 1px solid #BFDBFE;">
                <span style="font-size: 0.75rem; color: #1D4ED8; font-weight: 600;">TARGET CITIZEN LANGUAGE</span><br/>
                <span style="font-size: 1.05rem; font-weight: 700; color: #1E3A8A;">{tgt_info.get('flag','🇮🇳')} {tgt_info.get('name','')} ({tgt_info.get('native','')})</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_act:
        st.write("")
        process_btn = st.button("🚀 Process Document", type="primary", use_container_width=True)

    if process_btn:
        with st.spinner("🤖 Agent Controller orchestrating NLP pipeline..."):
            controller = AgenticNLPController(summarizer_model=SUMMARIZATION_MODELS[model_choice])
            result_state = controller.execute_workflow(
                document_input=st.session_state.current_doc_text,
                filename=st.session_state.doc_filename or "document.txt",
                target_language=target_lang_code,
            )
            st.session_state.workflow_state = result_state
            # Initialize QA engine with processed document text
            st.session_state.qa_engine = DocumentQAEngine(result_state.cleaned_text)
            st.success(f"Processing Complete in {result_state.total_latency_sec} seconds!")
            st.rerun()

# -------------------------------------------------------------
# RESULTS PRESENTATION
# -------------------------------------------------------------
if st.session_state.workflow_state is not None:
    state: WorkflowExecutionState = st.session_state.workflow_state

    st.markdown("---")
    render_kpi_metrics(state)

    # Multi-tab comprehensive display
    tab_res_sum, tab_res_trans, tab_res_info, tab_res_accuracy, tab_res_trace, tab_res_qa, tab_res_analytics = st.tabs([
        "📝 Summary",
        f"🌐 Translation ({state.target_language_name})",
        "🏷️ Key Information",
        "🎯 Evaluation & Accuracy",
        "🤖 Agent Trace",
        "💬 Citizen Q&A",
        "📊 Analytics & Export",
    ])

    # ---------------- TAB 1: SUMMARY ----------------
    with tab_res_sum:
        st.markdown("#### 📄 Executive Document Summary")
        st.info(state.executive_summary)

        st.markdown("#### 📌 Key Policy Highlights")
        for bp in state.bullet_points:
            st.markdown(f"- {bp}")

        col_c1, col_c2 = st.columns([1, 4])
        with col_c1:
            st.caption(f"Model: `{state.summarizer_model}`")

    # ---------------- TAB 2: TRANSLATION ----------------
    with tab_res_trans:
        st.markdown(f"#### 🌐 Translated Summary ({state.target_language_name} - {SUPPORTED_LANGUAGES.get(state.target_language_code, {}).get('native', '')})")
        st.success(state.translated_summary)

        if state.translated_bullet_points:
            st.markdown(f"#### 📌 {state.target_language_name} Highlights")
            for tbp in state.translated_bullet_points:
                st.markdown(f"- {tbp}")

        st.caption(f"Translation Engine: `{state.translation_backend}`")

    # ---------------- TAB 3: KEY INFORMATION ----------------
    with tab_res_info:
        render_key_information_card(state.extracted_entities)

    # ---------------- TAB 4: EVALUATION & ACCURACY ----------------
    with tab_res_accuracy:
        render_accuracy_metrics_view(state)

    # ---------------- TAB 5: AGENT TRACE ----------------
    with tab_res_trace:
        render_agent_trace(state.agent_trace)

    # ---------------- TAB 6: CITIZEN Q&A ----------------
    with tab_res_qa:
        st.markdown("#### 💬 Citizen Policy Assistant (Document Grounded Q&A)")
        st.caption("Ask specific eligibility, benefit, or procedural questions about this government document:")

        # Pre-set suggestion chips
        st.markdown("**Suggested Questions:**")
        chip_col1, chip_col2, chip_col3 = st.columns(3)
        with chip_col1:
            if st.button("❓ What are the financial benefits?", use_container_width=True):
                st.session_state.user_qa_input = "What are the financial benefits provided under this scheme?"
        with chip_col2:
            if st.button("❓ Who is eligible to apply?", use_container_width=True):
                st.session_state.user_qa_input = "Who is eligible to apply for this scheme?"
        with chip_col3:
            if st.button("❓ What documents are required?", use_container_width=True):
                st.session_state.user_qa_input = "What documents are required for application?"

        qa_query = st.text_input(
            "Enter your question:",
            value=st.session_state.get("user_qa_input", ""),
            placeholder="e.g. What is the target year and subsidy amount?",
        )

        if st.button("🔍 Get Answer", type="secondary"):
            if qa_query.strip() and st.session_state.qa_engine:
                qa_res = st.session_state.qa_engine.query(qa_query, target_lang=state.target_language_code)
                st.session_state.chat_history.append({
                    "question": qa_query,
                    "answer": qa_res["answer"],
                    "citation": qa_res["context_citation"],
                    "confidence": qa_res["confidence"],
                })

        # Display Chat History
        for chat in reversed(st.session_state.chat_history):
            st.markdown(f"**🙋 Citizen:** {chat['question']}")
            st.markdown(
                f"""
                <div style="background: #F0FDF4; border-left: 4px solid #10B981; padding: 0.8rem; border-radius: 4px; margin-bottom: 0.6rem;">
                    <b>🤖 Framework Answer ({state.target_language_name}):</b><br/>
                    {chat['answer']}<br/>
                    <small style="color: #64748B;">Grounding Confidence: {int(chat['confidence']*100)}%</small>
                </div>
                """,
                unsafe_allow_html=True,
            )
            with st.expander("🔍 View Context Citation from Document"):
                st.write(chat["citation"])

    # ---------------- TAB 6: ANALYTICS & EXPORT ----------------
    with tab_res_analytics:
        render_analytics_charts(state)

        st.markdown("---")
        st.markdown("### 📥 Download & Export Generated Report")
        col_ex1, col_ex2, col_ex3 = st.columns(3)

        with col_ex1:
            json_data = ReportExporter.to_json(state)
            st.download_button(
                label="📥 Download JSON Report",
                data=json_data,
                file_name=f"{state.document_name}_analysis.json",
                mime="application/json",
                use_container_width=True,
            )

        with col_ex2:
            md_data = ReportExporter.to_markdown(state)
            st.download_button(
                label="📥 Download Markdown / Text",
                data=md_data,
                file_name=f"{state.document_name}_summary.md",
                mime="text/markdown",
                use_container_width=True,
            )

        with col_ex3:
            pdf_data = ReportExporter.to_pdf_bytes(state)
            st.download_button(
                label="📥 Download PDF Summary Report",
                data=pdf_data,
                file_name=f"{state.document_name}_report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

else:
    # Helpful placeholder when no document is loaded yet
    st.info("👆 Please upload a government PDF / TXT document above, paste text, or load one of the sample government schemes from the left sidebar to start understanding!")
