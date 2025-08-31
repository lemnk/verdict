import os
from pathlib import Path
from typing import List
from jinja2 import Environment, FileSystemLoader, Template
import logging

from app.models.rag import RetrievalItem

logger = logging.getLogger(__name__)

# Initialize Jinja2 environment
template_dir = Path(__file__).parent.parent / "templates"
env = Environment(loader=FileSystemLoader(str(template_dir)))

def build_prompt(query: str, items: List[RetrievalItem]) -> str:
    """Build legal answer prompt using Jinja template"""
    try:
        # Load the legal answer template
        template = env.get_template("legal_answer.jinja")
        
        # Render template with query and retrieval items
        prompt = template.render(
            query=query,
            items=items
        )
        
        logger.info(f"Built prompt for query: {query[:50]}... with {len(items)} context items")
        return prompt
        
    except Exception as e:
        logger.error(f"Error building prompt: {str(e)}")
        # Fallback to simple prompt if template fails
        fallback_prompt = f"Question: {query}\n\nContext:\n"
        for i, item in enumerate(items, 1):
            fallback_prompt += f"[{i}] {item.snippet}\n\n"
        fallback_prompt += "Answer:"
        return fallback_prompt