"""
LangChain Tools for Agentic Error Analysis
These tools allow the AI agent to decide when and how to use various capabilities
"""
from langchain.tools import tool
from typing import Optional

from .classifier import ErrorClassifier
from .doc_fetcher import DocumentationFetcher


# Initialize shared instances
_classifier = ErrorClassifier()
_doc_fetcher = DocumentationFetcher()


@tool
def search_documentation(query: str, library: str = "") -> str:
    """
    Search for documentation about an error or programming concept.
    Use this when you need more information to solve an error.
    
    Args:
        query: What to search for (e.g., "NameError Response not defined django")
        library: Optional library name (e.g., "django", "fastapi", "python")
        
    Returns:
        Relevant documentation text
        
    Example:
        search_documentation("NameError Response not defined", "django")
    """
    if not _doc_fetcher.available:
        return "Documentation search not available. Please provide solution based on your knowledge."
    
    # Extract error type from query if present
    error_type = "unknown"
    if "error" in query.lower():
        for err in ["nameerror", "typeerror", "valueerror", "importerror", "attributeerror"]:
            if err in query.lower():
                error_type = err.replace("error", "")
                break
    
    try:
        docs = _doc_fetcher.fetch(
            error_msg=query,
            library=library,
            error_type=error_type
        )
        
        if docs:
            return f"Documentation found:\n{docs}"
        else:
            return "No specific documentation found. Use your general knowledge to help."
    except Exception as e:
        return f"Documentation search failed: {e}. Provide solution based on your knowledge."


@tool
def get_cached_solution(error_type: str) -> str:
    """
    Get a pre-cached solution for common, well-known errors.
    Use this for simple errors like ImportError, ConnectionError, MemoryError, etc.
    
    Args:
        error_type: Type of error (connection, import, memory, timeout, permission)
        
    Returns:
        Cached solution with fixes
        
    Example:
        get_cached_solution("import")
    """
    solution = _classifier.get_cached_solution(error_type.lower())
    
    if solution:
        fixes_text = "\n".join([f"- {fix}" for fix in solution.get('fixes', [])])
        return f"""Cached Solution Found:
Type: {solution.get('type', 'Unknown')}
Cause: {solution.get('cause', 'Unknown')}
Fixes:
{fixes_text}
"""
    else:
        return f"No cached solution for '{error_type}'. Try searching documentation or use your knowledge."


@tool
def detect_library_from_error(error_context: str) -> str:
    """
    Detect which library or framework is involved in the error.
    Use this to identify the technology stack before searching for documentation.
    
    Args:
        error_context: The error traceback and surrounding context
        
    Returns:
        Library name (e.g., "django", "fastapi", "numpy") or empty string
        
    Example:
        detect_library_from_error(traceback_text)
    """
    library = _doc_fetcher.detect_library(error_context)
    
    if library:
        return f"Detected library: {library}"
    else:
        return "No specific library detected. This appears to be a standard Python error."


@tool
def classify_error_type(error_context: str) -> str:
    """
    Classify the type of error from the context.
    Use this to understand what category of error you're dealing with.
    
    Args:
        error_context: The error logs and context
        
    Returns:
        Error type and whether it needs documentation
        
    Example:
        classify_error_type(error_logs)
    """
    error_type, needs_docs = _classifier.classify(error_context)
    
    recommendation = "Consider searching documentation" if needs_docs else "Can likely solve with cached knowledge"
    
    return f"""Error Classification:
Type: {error_type}
Complexity: {'Complex - ' + recommendation if needs_docs else 'Simple - ' + recommendation}
"""


# Export all tools
AGENT_TOOLS = [
    search_documentation,
    get_cached_solution,
    detect_library_from_error,
    classify_error_type
]
