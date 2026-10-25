import re
from pathlib import Path
import pymupdf as fitz  # PyMuPDF
import docx  # python-docx


class ParserServiceError(Exception):
    """Custom exception for resume document parsing errors."""
    pass


def clean_extracted_text(text: str) -> str:
    """Normalize whitespace and remove non-printable control characters."""
    if not text:
        return ""
    # Normalize Windows and Mac line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Remove control characters except standard tabs and newlines
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)
    # Collapse 3 or more newlines to 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_text_from_pdf(file_path: Path | str) -> tuple[str, bool]:
    """
    Extract selectable text from PDF using PyMuPDF.
    Returns: (cleaned_text, is_scanned_pdf)
    """
    path = Path(file_path)
    if not path.exists():
        raise ParserServiceError(f"File not found: {path.name}")

    try:
        doc = fitz.open(str(path))
    except Exception as e:
        raise ParserServiceError(f"Could not open PDF file. It may be corrupt or encrypted: {e}")

    extracted_pages = []
    total_chars = 0
    page_count = len(doc)

    try:
        for page_num in range(page_count):
            page = doc[page_num]
            text = page.get_text("text")
            if text:
                extracted_pages.append(text)
                total_chars += len(text.strip())
    except Exception as e:
        raise ParserServiceError(f"Error reading PDF content: {e}")
    finally:
        doc.close()

    full_text = "\n\n".join(extracted_pages)
    cleaned = clean_extracted_text(full_text)

    # Scanned PDF detection heuristic: document has pages but virtually no selectable text
    is_scanned = page_count > 0 and len(cleaned) < 50

    return cleaned, is_scanned


def extract_text_from_docx(file_path: Path | str) -> tuple[str, bool]:
    """
    Extract text from DOCX paragraphs and tables using python-docx.
    Returns: (cleaned_text, is_scanned_pdf=False)
    """
    path = Path(file_path)
    if not path.exists():
        raise ParserServiceError(f"File not found: {path.name}")

    try:
        doc = docx.Document(str(path))
    except Exception as e:
        raise ParserServiceError(f"Could not read DOCX document. It may be damaged: {e}")

    content_parts = []

    # Paragraphs
    for para in doc.paragraphs:
        t = para.text.strip()
        if t:
            content_parts.append(t)

    # Tables (often used in resumes for layout: Education, Skills, Work dates)
    for table in doc.tables:
        for row in table.rows:
            row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if row_cells:
                content_parts.append(" | ".join(dict.fromkeys(row_cells)))  # Deduplicate merged cells

    full_text = "\n".join(content_parts)
    cleaned = clean_extracted_text(full_text)

    return cleaned, False


def extract_resume_text(file_path: Path | str, file_type: str) -> tuple[str, bool]:
    """
    Unified entry point for extracting text from either PDF or DOCX.
    """
    ft = file_type.lower()
    if ft == "pdf":
        return extract_text_from_pdf(file_path)
    elif ft == "docx":
        return extract_text_from_docx(file_path)
    else:
        raise ParserServiceError(f"Unsupported file format '{file_type}'.")
