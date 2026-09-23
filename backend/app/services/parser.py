import io
import re
from typing import List, Dict, Any
import pymupdf as fitz  # PyMuPDF
import docx
from ..schemas import ParsedDocument

def clean_text(text: str) -> str:
    """Normalize whitespace and remove non-printable characters."""
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'\t', ' ', text)
    text = re.sub(r'[ \xa0]+', ' ', text)
    lines = [line.strip() for line in text.split('\n')]
    return '\n'.join([l for l in lines if l])

def parse_pdf(file_bytes: bytes, filename: str) -> ParsedDocument:
    """Extract text and metadata from PDF using PyMuPDF."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pages_text = []
    sections = []
    
    # Common section header patterns
    header_pattern = re.compile(
        r'^(experience|work experience|employment|education|skills|technical skills|projects|certifications|summary|objective|publications|awards)',
        re.IGNORECASE
    )

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        text = page.get_text("text")
        cleaned = clean_text(text)
        pages_text.append(cleaned)
        
        for line in cleaned.split('\n'):
            line_str = line.strip()
            if header_pattern.match(line_str) and len(line_str) < 40:
                if line_str not in sections:
                    sections.append(line_str)

    full_text = "\n\n".join(pages_text)
    return ParsedDocument(
        text=full_text,
        num_pages=len(doc),
        sections=sections,
        file_type="pdf",
        filename=filename
    )

def parse_docx(file_bytes: bytes, filename: str) -> ParsedDocument:
    """Extract text and metadata from DOCX using python-docx."""
    file_stream = io.BytesIO(file_bytes)
    doc = docx.Document(file_stream)
    paragraphs = []
    sections = []
    
    header_pattern = re.compile(
        r'^(experience|work experience|employment|education|skills|technical skills|projects|certifications|summary|objective)',
        re.IGNORECASE
    )

    for p in doc.paragraphs:
        t = p.text.strip()
        if t:
            paragraphs.append(t)
            if (p.style.name.startswith('Heading') or header_pattern.match(t)) and len(t) < 40:
                if t not in sections:
                    sections.append(t)

    full_text = "\n".join(paragraphs)
    return ParsedDocument(
        text=clean_text(full_text),
        num_pages=1,  # DOCX doesn't store explicit page counts without layout engine
        sections=sections,
        file_type="docx",
        filename=filename
    )

def parse_document(file_bytes: bytes, filename: str) -> ParsedDocument:
    ext = filename.lower().split('.')[-1]
    if ext == 'pdf':
        return parse_pdf(file_bytes, filename)
    elif ext in ['docx', 'doc']:
        return parse_docx(file_bytes, filename)
    elif ext in ['txt', 'md']:
        text = file_bytes.decode('utf-8', errors='ignore')
        return ParsedDocument(
            text=clean_text(text),
            num_pages=1,
            sections=[],
            file_type=ext,
            filename=filename
        )
    else:
        raise ValueError(f"Unsupported file format: .{ext}. Please upload a PDF or DOCX file.")
