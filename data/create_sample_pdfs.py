"""Generates sample government PDF files for testing and offline demo."""

import os
from src.ingestion.parser import DocumentParser


def create_pdf(filename: str, title: str, content: str):
    """Creates a basic valid PDF file."""
    lines = content.strip().split("\n")
    
    stream_lines = [
        "BT",
        "/F1 14 Tf",
        "40 750 Td",
        f"({title}) Tj",
        "/F2 9 Tf",
        "0 -20 Td",
        "12 TL",
    ]

    for line in lines:
        cleaned = line.strip().replace("(", "[").replace(")", "]").replace("\\", "")
        if not cleaned:
            stream_lines.append("T*")
            continue
        words = cleaned.split(" ")
        current = ""
        for w in words:
            if len(current) + len(w) > 85:
                stream_lines.append(f"({current}) '")
                current = w + " "
            else:
                current += w + " "
        if current:
            stream_lines.append(f"({current.strip()}) '")

    stream_lines.append("ET")
    stream_content = "\n".join(stream_lines)
    stream_bytes = stream_content.encode("latin-1", errors="replace")
    stream_len = len(stream_bytes)

    pdf_template = (
        "%PDF-1.4\n"
        "1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        "2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        "3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R /F2 6 0 R >> >> >>\nendobj\n"
        f"4 0 obj\n<< /Length {stream_len} >>\nstream\n{stream_content}\nendstream\nendobj\n"
        "5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>\nendobj\n"
        "6 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
        "xref\n0 7\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000244 00000 n \n0000000350 00000 n \n0000000450 00000 n \n"
        "trailer\n<< /Size 7 /Root 1 0 R >>\nstartxref\n550\n%%EOF\n"
    )

    with open(filename, "wb") as f:
        f.write(pdf_template.encode("latin-1", errors="replace"))
    print(f"Created: {filename}")


if __name__ == "__main__":
    docs = [
        ("data/sample_documents/pmay_scheme.pdf", "PRADHAN MANTRI AWAS YOJANA (PMAY)", "data/sample_documents/pmay_scheme.txt"),
        ("data/sample_documents/pm_kisan_policy.pdf", "PM-KISAN SAMMAN NIDHI", "data/sample_documents/pm_kisan_policy.txt"),
        ("data/sample_documents/ayushman_bharat.pdf", "AYUSHMAN BHARAT (PM-JAY)", "data/sample_documents/ayushman_bharat.txt"),
        ("data/sample_documents/nep_2020.pdf", "NATIONAL EDUCATION POLICY 2020", "data/sample_documents/nep_2020.txt"),
    ]

    for pdf_path, title, txt_path in docs:
        if os.path.exists(txt_path):
            with open(txt_path, "r", encoding="utf-8") as f:
                content = f.read()
            create_pdf(pdf_path, title, content)
