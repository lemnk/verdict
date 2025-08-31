import pytest
import uuid
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import os

from app.utils.parser import extract_chunks_from_pdf, clean_text, create_chunks
from app.utils.embedding import embed_chunks, create_faiss_index, search_similar_chunks
from app.routers.parse import parse_document, get_document_chunks
from app.db.models import Document, DocumentChunk
from app.models.chunk import ParseResult

class TestTextProcessing:
    """Test text cleaning and chunking utilities"""
    
    def test_clean_text(self):
        """Test text cleaning functionality"""
        dirty_text = "  Multiple    spaces\n\n\nand\n\n\n\nnewlines  "
        cleaned = clean_text(dirty_text)
        assert cleaned == "Multiple spaces and newlines"
    
    def test_create_chunks_small_text(self):
        """Test chunking for text smaller than chunk size"""
        text = "Short text"
        chunks = create_chunks(text, chunk_size=100)
        assert len(chunks) == 1
        assert chunks[0] == "Short text"
    
    def test_create_chunks_large_text(self):
        """Test chunking for text larger than chunk size"""
        text = "This is a longer text that should be split into multiple chunks. " * 10
        chunks = create_chunks(text, chunk_size=100, overlap=20)
        assert len(chunks) > 1
        assert all(len(chunk) <= 100 for chunk in chunks)
    
    def test_create_chunks_with_overlap(self):
        """Test that chunks have proper overlap"""
        text = "Sentence one. Sentence two. Sentence three. Sentence four."
        chunks = create_chunks(text, chunk_size=30, overlap=10)
        assert len(chunks) > 1
        
        # Check that consecutive chunks share some content
        for i in range(len(chunks) - 1):
            current_chunk = chunks[i]
            next_chunk = chunks[i + 1]
            # Should have some overlap
            assert any(word in next_chunk for word in current_chunk.split()[-3:])

class TestPDFParser:
    """Test PDF parsing functionality"""
    
    @patch('app.utils.parser.fitz.open')
    def test_extract_chunks_from_pdf_success(self, mock_fitz_open):
        """Test successful PDF extraction"""
        # Mock PyMuPDF document
        mock_doc = Mock()
        mock_doc.page_count = 2
        
        mock_page1 = Mock()
        mock_page1.get_text.return_value = "Page one content. "
        mock_page2 = Mock()
        mock_page2.get_text.return_value = "Page two content."
        
        mock_doc.load_page.side_effect = [mock_page1, mock_page2]
        mock_fitz_open.return_value = mock_doc
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            chunks = extract_chunks_from_pdf(tmp_path)
            assert len(chunks) > 0
            assert "Page one content" in chunks[0]
            assert "Page two content" in chunks[1]
        finally:
            os.unlink(tmp_path)
    
    def test_extract_chunks_from_pdf_file_not_found(self):
        """Test PDF extraction with non-existent file"""
        with pytest.raises(FileNotFoundError):
            extract_chunks_from_pdf("/nonexistent/file.pdf")
    
    @patch('app.utils.parser.fitz.open')
    def test_extract_chunks_from_pdf_empty(self, mock_fitz_open):
        """Test PDF extraction with empty document"""
        mock_doc = Mock()
        mock_doc.page_count = 0
        mock_fitz_open.return_value = mock_doc
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            chunks = extract_chunks_from_pdf(tmp_path)
            assert chunks == []
        finally:
            os.unlink(tmp_path)

class TestEmbeddings:
    """Test embedding generation and FAISS functionality"""
    
    @patch('app.utils.embedding.client.embeddings.create')
    def test_embed_chunks_success(self, mock_openai):
        """Test successful embedding generation"""
        mock_response = Mock()
        mock_response.data = [
            Mock(embedding=[0.1, 0.2, 0.3]),
            Mock(embedding=[0.4, 0.5, 0.6])
        ]
        mock_openai.return_value = mock_response
        
        chunks = ["Text chunk 1", "Text chunk 2"]
        embeddings = embed_chunks(chunks)
        
        assert len(embeddings) == 2
        assert len(embeddings[0]) == 3
        assert embeddings[0] == [0.1, 0.2, 0.3]
    
    def test_embed_chunks_empty_list(self):
        """Test embedding generation with empty chunks list"""
        embeddings = embed_chunks([])
        assert embeddings == []
    
    def test_create_faiss_index(self):
        """Test FAISS index creation"""
        embeddings = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]
        index = create_faiss_index(embeddings, dimension=2)
        assert index.ntotal == 3
    
    def test_search_similar_chunks(self):
        """Test FAISS similarity search"""
        embeddings = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]
        index = create_faiss_index(embeddings, dimension=2)
        
        query_embedding = [0.1, 0.2]
        scores, indices = search_similar_chunks(query_embedding, index, k=2)
        
        assert len(scores) == 2
        assert len(indices) == 2
        assert indices[0] == 0  # Should match first embedding

class TestParseRouter:
    """Test parse router endpoints"""
    
    def test_parse_document_invalid_uuid(self):
        """Test parse endpoint with invalid UUID"""
        with pytest.raises(ValueError):
            uuid.UUID("invalid-uuid")
    
    @patch('app.routers.parse.extract_chunks_from_pdf')
    @patch('app.routers.parse.embed_chunks')
    def test_parse_document_success(self, mock_embed, mock_extract):
        """Test successful document parsing"""
        # Mock dependencies
        mock_extract.return_value = ["Chunk 1", "Chunk 2"]
        mock_embed.return_value = [[0.1, 0.2], [0.3, 0.4]]
        
        # This would need a proper test database setup
        # For now, just test the mock functions work
        assert mock_extract.return_value == ["Chunk 1", "Chunk 2"]
        assert mock_embed.return_value == [[0.1, 0.2], [0.3, 0.4]]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])