# 🏛️ An Agentic NLP Framework for Multilingual Government Document Understanding

![Project Status](https://img.shields.io/badge/Status-Complete-success)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Framework](https://img.shields.io/badge/Framework-Streamlit-FF4B4B)
![NLP](https://img.shields.io/badge/NLP-Transformers%20%7C%20PyTorch-orange)
![Institution](https://img.shields.io/badge/Institution-BMSCE%20%2F%20VTU-navy)

**B.E. Final Major Project (Artificial Intelligence & Data Science)**  
*Department of Artificial Intelligence & Data Science, BMS College of Engineering, Bengaluru*  
*Affiliated to Visvesvaraya Technological University (VTU), Belagavi*

---

## 👥 Authors & Supervision

- **Pallavi** (1BM23AD041)
- **Shivani Agrawal** (1BM23AD058)
- **Vaibhavi K** (1BM22AD065)

**Project Guide:** Prof. Sangeetha S (*Assistant Professor, Dept. of AI & DS, BMSCE*)  
**Head of Department:** Dr. Indiramma M (*Professor & Head, Dept. of AI & DS, BMSCE*)

---

## 📖 Executive Overview

Government organizations publish a large volume of policies, schemes, circulars, notifications, and legal documents to communicate critical benefits to citizens. However, these documents are typically lengthy, dense with bureaucratic terminology, and available in limited formats.

This project implements an end-to-end **Agentic NLP Framework** that automates the understanding, summarization, translation, and structured entity extraction of government communications. Coordinated by an **Agentic AI Controller**, the system converts complex documents into citizen-friendly summaries in multiple Indian regional languages and enables interactive conversational Q&A.

---

## 🌟 Key Sub-systems & Features

1. **📄 Document Ingestion & Preprocessing (`src/ingestion/`)**:
   - Universal parsing for digital PDFs (`PyPDF2`) and plain text files.
   - Text cleaning, noise suppression, and Unicode normalization (NFC) for Indic scripts.
   - Smart chunking with sentence boundary preservation.

2. **🔍 Automatic Language & Script Detection (`src/language/`)**:
   - High-accuracy detection of source document languages: English, Hindi, Kannada, Tamil, Telugu, Marathi, Bengali, Gujarati, Malayalam.
   - Script distribution analysis and confidence scoring.

3. **🤖 Agentic AI Controller (`src/agent/`)**:
   - Multi-step workflow orchestration (Context Analysis -> Planning -> Execution -> Validation).
   - Real-time decision logs & latency breakdown trace for full transparency.

4. **📝 Transformer-Based Abstractive Summarization (`src/summarization/`)**:
   - Transformer pipelines (`facebook/bart-large-cnn`, `google/flan-t5-small`, `sshleifer/distilbart-cnn-12-6`, `t5-small`).
   - Executive summaries, plain-language citizen digests, and structured policy bullet points.

5. **🌐 Multilingual Translation Sub-system (`src/translation/`)**:
   - Fast translation into 8+ Indian regional languages (Hindi, Kannada, Tamil, Telugu, Marathi, Bengali, Gujarati, Malayalam).
   - Neural translation engine with offline domain glossary fallback and memory caching.

6. **🏷️ Key Information Extraction (`src/extraction/`)**:
   - Structured schema extraction: Scheme Title, Acronym, Sponsoring Ministry, Objectives, Target Year, Financial Benefits/Subsidies, Eligibility Criteria, Coverage, Required Documents, and Helpline Portals.

7. **💬 Citizen Document Grounded Q&A Assistant (`src/qa/`)**:
   - Interactive RAG chatbot answering citizen queries directly with citations from the document.

8. **📊 Analytics Dashboard & Export Engine (`src/analytics/` & `src/export/`)**:
   - Text compression ratio charts and execution latency distribution.
   - One-click export of full reports in **PDF**, **JSON**, and **Markdown/Text** formats.

---

## 🏗️ System Architecture

```
                               ┌──────────────────────────┐
                               │       User / Citizen     │
                               └────────────┬─────────────┘
                                            │ Uploads PDF / TXT
                                            ▼
                               ┌──────────────────────────┐
                               │   Streamlit Web Interface │
                               └────────────┬─────────────┘
                                            │
                                            ▼
                          ┌────────────────────────────────────┐
                          │    Data Ingestion & Preprocessing  │
                          └─────────────────┬──────────────────┘
                                            │
                                            ▼
                          ┌────────────────────────────────────┐
                          │      Language & Script Detector    │
                          └─────────────────┬──────────────────┘
                                            │
                                            ▼
                     ┌──────────────────────────────────────────────┐
                     │         Agentic AI Controller (Brain)        │
                     │  - Dynamic Workflow Planning & Intent        │
                     │  - Task Orchestration & Tool Sequencing     │
                     └───────┬──────────────┬──────────────┬────────┘
                             │              │              │
        ┌────────────────────┴──┐   ┌───────┴──────┐  ┌────┴─────────────────┐
        │  Transformer BART/T5  │   │  Named Entity│  │    Multilingual      │
        │      Summarizer       │   │  Extraction  │  │  Translation Engine  │
        └────────────────────┬──┘   └───────┬──────┘  └────┬─────────────────┘
                             │              │              │
                             └──────────────┼──────────────┘
                                            │
                                            ▼
                          ┌────────────────────────────────────┐
                          │   Validation & Result Generation   │
                          └─────────────────┬──────────────────┘
                                            │
                    ┌───────────────────────┼───────────────────────┐
                    ▼                       ▼                       ▼
          [ Summary & Highlights ]  [ Translated Output ]  [ Key Entity Schema ]
          [ Citizen Q&A Assistant]  [ Analytics Dashboard]  [ PDF / JSON Export ]
```

---

## 📁 Repository Structure

```
noble-rutherford/
├── app.py                      # Main Streamlit Application
├── requirements.txt            # Python dependencies
├── README.md                   # Complete documentation
├── data/
│   └── sample_documents/       # Pre-packaged government policy documents
│       ├── pmay_scheme.txt     # Pradhan Mantri Awas Yojana
│       ├── pm_kisan_policy.txt # PM-KISAN Samman Nidhi
│       ├── ayushman_bharat.txt # Ayushman Bharat PM-JAY
│       ├── nep_2020.txt        # National Education Policy 2020
│       ├── pm_kisan_hindi.txt  # PM-KISAN in Hindi
│       └── gruha_lakshmi_kannada.txt # Gruha Lakshmi in Kannada
├── src/
│   ├── config.py               # Settings & language dictionaries
│   ├── agent/                  # Agentic Controller & Workflow State
│   │   ├── controller.py
│   │   └── workflow_state.py
│   ├── ingestion/              # PDF/TXT Parsers & Cleaners
│   │   ├── parser.py
│   │   └── preprocessor.py
│   ├── language/               # Language & Script Detection
│   │   └── detector.py
│   ├── summarization/          # BART & T5 Summarizers
│   │   └── summarizer.py
│   ├── translation/            # Regional Translators & Glossaries
│   │   └── translator.py
│   ├── extraction/             # NER & Key Information Extractor
│   │   └── extractor.py
│   ├── qa/                     # Citizen Document Q&A RAG Engine
│   │   └── rag_engine.py
│   ├── export/                 # PDF, JSON, and MD Exporters
│   │   └── exporter.py
│   └── ui/                     # UI components, cards, and CSS styles
│       ├── components.py
│       └── styles.py
└── tests/                      # Automated Unit Test Suite
    ├── test_ingestion.py
    ├── test_detector.py
    ├── test_summarizer.py
    ├── test_extractor.py
    ├── test_translator.py
    ├── test_controller.py
    └── test_qa.py
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13
- Git

### 2. Installation
Clone the repository and install required packages:
```bash
git clone <repo-url>
cd noble-rutherford
pip install -r requirements.txt
```

### 3. Running the Streamlit Application
Launch the interactive web platform:
```bash
streamlit run app.py
```
Open your web browser at `http://localhost:8501`.

### 4. Running Automated Unit Tests
Execute the comprehensive test suite:
```bash
python3 -m unittest discover tests/
```

---

## 📊 Sample Datasets & Demos
The project includes pre-loaded official government schemes for evaluation:
1. **Pradhan Mantri Awas Yojana (PMAY)**: Affordable housing scheme.
2. **PM-KISAN Samman Nidhi**: Direct financial support to farmers.
3. **Ayushman Bharat (PM-JAY)**: Universal healthcare coverage.
4. **National Education Policy (NEP 2020)**: Education reform framework.
5. **PM-KISAN (Hindi)**: Hindi language input demo.
6. **Gruha Lakshmi (Kannada)**: Regional welfare scheme in Kannada.
