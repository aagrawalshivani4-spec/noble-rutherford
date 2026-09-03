"""
Document Ingestion Module: Supports PDF and plain text formats.
"""

import io
from typing import Dict, Any, Union
import PyPDF2


class DocumentParser:
    """Parses uploaded PDF and TXT files and extracts structured text."""

    @staticmethod
    def parse_txt(file_content: Union[str, bytes]) -> Dict[str, Any]:
        """Parses plain text document."""
        if isinstance(file_content, bytes):
            # Try utf-8 first, fallback to latin-1
            try:
                text = file_content.decode("utf-8")
            except UnicodeDecodeError:
                text = file_content.decode("latin-1", errors="ignore")
        else:
            text = file_content

        lines = [line.strip() for line in text.split("\n") if line.strip()]
        return {
            "format": "TXT",
            "page_count": 1,
            "raw_text": text,
            "line_count": len(lines),
            "char_count": len(text),
            "word_count": len(text.split()),
            "pages": [{"page_num": 1, "text": text}],
        }

    @staticmethod
    def parse_pdf(file_bytes_or_path: Union[bytes, io.BytesIO, str]) -> Dict[str, Any]:
        """Extracts text and page-by-page content from PDF document."""
        if isinstance(file_bytes_or_path, (bytes, bytearray)):
            stream = io.BytesIO(file_bytes_or_path)
        elif isinstance(file_bytes_or_path, str):
            stream = open(file_bytes_or_path, "rb")
        else:
            stream = file_bytes_or_path

        try:
            reader = PyPDF2.PdfReader(stream)
            num_pages = len(reader.pages)
            pages_content = []
            full_text_list = []

            for idx, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text() or ""
                except Exception:
                    page_text = ""
                page_text = page_text.strip()
                pages_content.append({"page_num": idx + 1, "text": page_text})
                if page_text:
                    full_text_list.append(page_text)

            if isinstance(file_bytes_or_path, str) and hasattr(stream, "close"):
                stream.close()

            full_text = "\n\n".join(full_text_list)
            lines = [line.strip() for line in full_text.split("\n") if line.strip()]

            return {
                "format": "PDF",
                "page_count": num_pages,
                "raw_text": full_text,
                "line_count": len(lines),
                "char_count": len(full_text),
                "word_count": len(full_text.split()),
                "pages": pages_content,
            }
        except Exception as e:
            return {
                "format": "PDF",
                "page_count": 0,
                "raw_text": "",
                "line_count": 0,
                "char_count": 0,
                "word_count": 0,
                "pages": [],
                "error": str(e),
            }

    @classmethod
    def parse(cls, file_obj, filename: str = "") -> Dict[str, Any]:
        """Universal entrypoint for document ingestion."""
        if isinstance(file_obj, dict) and "raw_text" in file_obj:
            return file_obj

        name_lower = filename.lower()
        if name_lower.endswith(".pdf"):
            if hasattr(file_obj, "read"):
                return cls.parse_pdf(file_obj.read())
            return cls.parse_pdf(file_obj)
        else:
            if hasattr(file_obj, "read"):
                content = file_obj.read()
                return cls.parse_txt(content)
            return cls.parse_txt(file_obj)
