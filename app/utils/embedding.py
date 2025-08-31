import os
from typing import List
import numpy as np
import logging
from openai import OpenAI
import faiss
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_embedding(text: str) -> List[float]:
    """Generate a single embedding. Thin wrapper around embed_chunks for parity with callers."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("text must be a non-empty string")
    vecs = embed_chunks([text])
    if not vecs or not isinstance(vecs[0], list):
        raise RuntimeError("embedding backend returned an empty or invalid vector")
    return vecs[0]

def embed_chunks(chunks: List[str]) -> List[List[float]]:
    """Generate embeddings for text chunks using OpenAI text-embedding-3-small"""
    if not chunks:
        return []
    
    try:
        # Batch process chunks for efficiency
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=chunks
        )
        
        embeddings = [data.embedding for data in response.data]
        logger.info(f"Generated embeddings for {len(chunks)} chunks")
        return embeddings
        
    except Exception as e:
        logger.error(f"Error generating embeddings: {str(e)}")
        raise

def create_faiss_index(embeddings: List[List[float]], dimension: int = 1536) -> faiss.Index:
    """Create FAISS index for vector similarity search"""
    try:
        # Convert to numpy array
        vectors = np.array(embeddings).astype('float32')
        
        # Create FAISS index
        index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        index.add(vectors)
        
        logger.info(f"Created FAISS index with {len(embeddings)} vectors")
        return index
        
    except Exception as e:
        logger.error(f"Error creating FAISS index: {str(e)}")
        raise

def search_similar_chunks(query_embedding: List[float], index: faiss.Index, k: int = 5) -> tuple:
    """Search for similar chunks using FAISS index"""
    try:
        query_vector = np.array([query_embedding]).astype('float32')
        scores, indices = index.search(query_vector, k)
        
        return scores[0].tolist(), indices[0].tolist()
        
    except Exception as e:
        logger.error(f"Error searching FAISS index: {str(e)}")
        raise

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)