import os
import time
from typing import Dict, Any
from openai import OpenAI
from fastapi import HTTPException
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Default pricing (per 1K tokens)
DEFAULT_PRICE_IN = 0.30
DEFAULT_PRICE_OUT = 1.20
DEFAULT_MODEL = "gpt-4o-mini"

def get_openai_config() -> Dict[str, Any]:
    """Get OpenAI configuration from environment variables"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="LLM unavailable - no API key")
    
    return {
        "api_key": api_key,
        "model": os.getenv("OPENAI_MODEL", DEFAULT_MODEL),
        "price_in": float(os.getenv("OPENAI_PRICE_IN", DEFAULT_PRICE_IN)),
        "price_out": float(os.getenv("OPENAI_PRICE_OUT", DEFAULT_PRICE_OUT))
    }

def chat_complete(prompt: str, model: str = None) -> Dict[str, Any]:
    """Complete chat using OpenAI API with cost and latency tracking"""
    start_time = time.time()
    
    try:
        config = get_openai_config()
        client = OpenAI(api_key=config["api_key"])
        
        # Use provided model or default
        model_to_use = model or config["model"]
        
        # Make API call
        response = client.chat.completions.create(
            model=model_to_use,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Low temperature for consistent legal answers
            max_tokens=1000
        )
        
        # Calculate metrics
        latency_ms = (time.time() - start_time) * 1000
        tokens_in = response.usage.prompt_tokens
        tokens_out = response.usage.completion_tokens
        
        # Calculate cost
        cost_usd = (tokens_in * config["price_in"] / 1000) + (tokens_out * config["price_out"] / 1000)
        
        result = {
            "text": response.choices[0].message.content,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "cost_usd": round(cost_usd, 6),
            "latency_ms": round(latency_ms, 2),
            "model": model_to_use,
            "provider": "openai"
        }
        
        logger.info(f"LLM completion: {tokens_in}+{tokens_out} tokens, ${cost_usd:.6f}, {latency_ms:.2f}ms")
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error in chat_complete: {str(e)}")
        raise HTTPException(status_code=503, detail=f"LLM service error: {str(e)}")