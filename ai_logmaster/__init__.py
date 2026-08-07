"""
AI LogMaster - Smart error analysis tool with AI-powered solutions
"""
from .core.analyzer import ErrorAnalyzer, analyze_error
from .core.agent import Agent
from .core.classifier import ErrorClassifier
from .core.doc_fetcher import DocumentationFetcher
from .core.llm_client import LLMClient
__version__ = "1.3.1"

__all__ = [
    'ErrorAnalyzer',
    'Agent',
    'ErrorClassifier',
    'DocumentationFetcher',
    'LLMClient',
    'analyze_error',  # Backward compatibility
]
