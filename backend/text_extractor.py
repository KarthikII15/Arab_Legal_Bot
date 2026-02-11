"""
Text Extractor for Arabic Legal Documents.

Extracts plain text from PDF and DOCX files for downstream analysis.
Supports:
- PDF via PyMuPDF (fitz) — handles Arabic/RTL text
- DOCX via python-docx — handles paragraphs and tables
- TXT — direct passthrough
"""

import os
import logging

logger = logging.getLogger(__name__)


def extract_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF bytes using PyMuPDF."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise ImportError("PyMuPDF not installed. Run: pip install pymupdf")
    
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text_parts = []
    seen_content = set() # To detect duplicate repeated pages
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text").strip()
        
        if text:
            # Hash or simplify text to detect identical content
            # (In legal docs, identical pages are usually error templates)
            content_fingerprint = " ".join(text.split())[:1000] # Normalize for comparison
            if content_fingerprint not in seen_content:
                text_parts.append(text)
                seen_content.add(content_fingerprint)
            else:
                logger.warning(f"Skipping duplicate page {page_num+1} in PDF")
    
    full_text = "\n\n".join(text_parts)
    logger.info(f"Extracted {len(full_text)} chars from {len(text_parts)} unique pages (Total: {len(doc)})")
    doc.close()
    return full_text


def extract_from_docx(file_bytes: bytes) -> str:
    """Extract text from DOCX bytes using python-docx."""
    try:
        from docx import Document
    except ImportError:
        raise ImportError("python-docx not installed. Run: pip install python-docx")
    
    import io
    doc = Document(io.BytesIO(file_bytes))
    
    text_parts = []
    
    # Extract paragraphs
    for para in doc.paragraphs:
        if para.text.strip():
            text_parts.append(para.text.strip())
    
    # Extract table content (legal docs often have tables)
    for table in doc.tables:
        for row in table.rows:
            row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
            if row_text:
                text_parts.append(row_text)
    
    full_text = "\n".join(text_parts)
    logger.info(f"Extracted {len(full_text)} chars from DOCX ({len(doc.paragraphs)} paragraphs)")
    return full_text


def extract_text(filename: str, file_bytes: bytes) -> str:
    """
    Extract text from a file based on its extension.
    
    Args:
        filename: Original filename (used to detect type)
        file_bytes: Raw file content
        
    Returns:
        Extracted plain text
        
    Raises:
        ValueError: If file type is not supported
    """
    ext = os.path.splitext(filename)[1].lower()
    
    if ext == ".pdf":
        return extract_from_pdf(file_bytes)
    elif ext in (".docx",):
        return extract_from_docx(file_bytes)
    elif ext in (".txt", ".text"):
        # Try UTF-8 first, fall back to cp1256 (common Arabic encoding)
        try:
            return file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return file_bytes.decode("cp1256", errors="replace")
    else:
        raise ValueError(f"Unsupported file type: {ext}. Supported: .pdf, .docx, .txt")
