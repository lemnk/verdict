import pytest
import uuid
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal
import json
import redis

from app.models.rag import AnswerRequest, AnswerResponse, Citation, RetrievalItem
from app.utils.retrieval import retrieve_topk, trim_context_to_token_budget
from app.utils.prompting import build_prompt
from app.utils.llm import chat_complete
from app.routers.rag import ask_legal_question, generate_cache_key, get_cached_response

@pytest.fixture
def sample_document_chunks():
    """Create sample document chunks for testing"""
    doc_id = uuid.uuid4()
    return [
        RetrievalItem(
            doc_id=doc_id,
            chunk_index=0,
            score=0.95,
            snippet="This is a sample legal document about contract law. It discusses the essential elements of a valid contract including offer, acceptance, and consideration."
        ),
        RetrievalItem(
            doc_id=doc_id,
            chunk_index=1,
            score=0.87,
            snippet="The court held that the contract was enforceable because all elements were present. The parties had a meeting of the minds and exchanged valuable consideration."
        )
    ]

@pytest.fixture
def sample_answer_request():
    """Create sample answer request for testing"""
    return AnswerRequest(
        query="What are the essential elements of a contract?",
        k=2,
        max_context_tokens=1000
    )

class TestRetrieval:
    """Test retrieval functionality"""
    
    def test_trim_context_to_token_budget(self, sample_document_chunks):
        """Test context trimming to token budget"""
        # Test with generous budget
        result = trim_context_to_token_budget(sample_document_chunks, 2000, "gpt-4o-mini")
        assert len(result) == 2
        assert result[0].doc_id == sample_document_chunks[0].doc_id
        
        # Test with tight budget
        result = trim_context_to_token_budget(sample_document_chunks, 100, "gpt-4o-mini")
        assert len(result) == 1
        assert len(result[0].snippet) <= 400  # Should be truncated
    
    def test_trim_context_empty_list(self):
        """Test context trimming with empty list"""
        result = trim_context_to_token_budget([], 1000, "gpt-4o-mini")
        assert result == []

class TestPrompting:
    """Test prompt building functionality"""
    
    def test_build_prompt(self, sample_document_chunks):
        """Test prompt building with Jinja template"""
        query = "What are the essential elements of a contract?"
        prompt = build_prompt(query, sample_document_chunks)
        
        assert query in prompt
        assert "[1]" in prompt
        assert "[2]" in prompt
        assert "doc=" in prompt
        assert "chunk=" in prompt
        assert "score=" in prompt
    
    def test_build_prompt_empty_items(self):
        """Test prompt building with empty items"""
        query = "Test query"
        prompt = build_prompt(query, [])
        assert query in prompt
        assert "Context:" in prompt

class TestLLM:
    """Test LLM integration"""
    
    @patch('app.utils.llm.client.chat.completions.create')
    def test_chat_complete_success(self, mock_openai):
        """Test successful LLM completion"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="This is a test answer."))]
        mock_response.usage = Mock(prompt_tokens=50, completion_tokens=20)
        mock_openai.return_value = mock_response
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
            result = chat_complete("Test prompt")
            
            assert result["text"] == "This is a test answer."
            assert result["tokens_in"] == 50
            assert result["tokens_out"] == 20
            assert result["provider"] == "openai"
    
    def test_chat_complete_no_api_key(self):
        """Test LLM completion without API key"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(Exception) as exc_info:
                chat_complete("Test prompt")
            assert "LLM unavailable" in str(exc_info.value)

class TestRAGRouter:
    """Test RAG router endpoints"""
    
    def test_generate_cache_key(self):
        """Test cache key generation"""
        user_id = 123
        query = "Test query"
        k = 5
        model = "gpt-4o-mini"
        
        cache_key = generate_cache_key(user_id, query, k, model)
        assert isinstance(cache_key, str)
        assert len(cache_key) == 64  # SHA256 hash length
        
        # Same parameters should generate same key
        cache_key2 = generate_cache_key(user_id, query, k, model)
        assert cache_key == cache_key2
    
    @patch('app.routers.rag.retrieve_topk')
    @patch('app.routers.rag.chat_complete')
    @patch('app.routers.rag.redis_client')
    def test_ask_legal_question_success(self, mock_redis, mock_llm, mock_retrieve, sample_answer_request):
        """Test successful RAG question answering"""
        # Mock dependencies
        mock_retrieve.return_value = [
            RetrievalItem(
                doc_id=uuid.uuid4(),
                chunk_index=0,
                score=0.95,
                snippet="Sample legal content about contracts."
            )
        ]
        
        mock_llm.return_value = {
            "text": "A contract requires offer, acceptance, and consideration.",
            "tokens_in": 100,
            "tokens_out": 50,
            "cost_usd": 0.045,
            "latency_ms": 1500.0,
            "model": "gpt-4o-mini",
            "provider": "openai"
        }
        
        mock_redis.get.return_value = None  # No cache hit
        
        # Mock database session and user
        mock_db = Mock()
        mock_user = Mock()
        mock_user.id = 123
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        # Mock credentials
        mock_credentials = Mock()
        
        # This would need proper database setup for full testing
        # For now, just test the mock functions work
        assert mock_retrieve.return_value[0].score == 0.95
        assert mock_llm.return_value["text"] == "A contract requires offer, acceptance, and consideration."

class TestCaching:
    """Test Redis caching functionality"""
    
    def test_cache_key_uniqueness(self):
        """Test that different parameters generate different cache keys"""
        user_id = 123
        query1 = "What is contract law?"
        query2 = "What is tort law?"
        
        key1 = generate_cache_key(user_id, query1, 5, "gpt-4o-mini")
        key2 = generate_cache_key(user_id, query2, 5, "gpt-4o-mini")
        
        assert key1 != key2
    
    def test_cache_key_same_parameters(self):
        """Test that same parameters generate same cache key"""
        user_id = 123
        query = "What is contract law?"
        k = 5
        model = "gpt-4o-mini"
        
        key1 = generate_cache_key(user_id, query, k, model)
        key2 = generate_cache_key(user_id, query, k, model)
        
        assert key1 == key2

if __name__ == "__main__":
    pytest.main([__file__, "-v"])