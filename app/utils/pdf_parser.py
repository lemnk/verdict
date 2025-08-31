import PyPDF2
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

def parse_pdf_document(file_path: str) -> Dict[str, Any]:
    """Extract text and metadata from PDF legal document"""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            text_content = ""
            for page in pdf_reader.pages:
                text_content += page.extract_text()
            
            metadata = {
                "num_pages": len(pdf_reader.pages),
                "title": pdf_reader.metadata.get('/Title', ''),
                "author": pdf_reader.metadata.get('/Author', ''),
                "subject": pdf_reader.metadata.get('/Subject', '')
            }
            
            return {
                "text": text_content,
                "metadata": metadata,
                "success": True
            }
            
    except Exception as e:
        logger.error(f"Error parsing PDF {file_path}: {str(e)}")
        return {
            "text": "",
            "metadata": {},
            "success": False,
            "error": str(e)
        }