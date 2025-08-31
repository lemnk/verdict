import fitz  # PyMuPDF
import re
from typing import List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """Clean extracted text by removing extra whitespace and normalizing"""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove page numbers and headers
    text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
    # Strip leading/trailing whitespace
    text = text.strip()
    return text

def create_chunks(text: str, chunk_size: int = 600, overlap: int = 100) -> List[str]:
    """Split text into overlapping chunks of specified size"""
    if len(text) <= chunk_size:
        return [text] if text.strip() else []
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at sentence boundaries
        if end < len(text):
            # Look for sentence endings within the last 100 characters
            search_start = max(start + chunk_size - 100, start)
            sentence_end = text.rfind('.', search_start, end)
            if sentence_end > start + chunk_size // 2:  # Only break if we find a reasonable sentence boundary
                end = sentence_end + 1
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position with overlap
        start = end - overlap
        if start >= len(text):
            break
    
    return chunks

def extract_chunks_from_pdf(pdf_path: str, chunk_size: int = 600, overlap: int = 100) -> List[str]:
    """Extract text from PDF and split into chunks"""
    try:
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Open PDF with PyMuPDF
        doc = fitz.open(pdf_path)
        
        if doc.page_count == 0:
            logger.warning(f"PDF has no pages: {pdf_path}")
            return []
        
        # Extract text from all pages
        full_text = ""
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text = page.get_text()
            full_text += text + " "
        
        doc.close()
        
        # Clean the extracted text
        cleaned_text = clean_text(full_text)
        
        if not cleaned_text:
            logger.warning(f"No text extracted from PDF: {pdf_path}")
            return []
        
        # Create chunks
        chunks = create_chunks(cleaned_text, chunk_size, overlap)
        
        logger.info(f"Extracted {len(chunks)} chunks from {pdf_path}")
        return chunks
        
    except Exception as e:
        logger.error(f"Error extracting chunks from PDF {pdf_path}: {str(e)}")
        raise