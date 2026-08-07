"""
Documentation Fetcher - Dynamic documentation retrieval from web
"""
import json
import os
import re
from typing import Optional


class DocumentationFetcher:
    """Fetches relevant documentation dynamically based on errors"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize DocumentationFetcher
        
        Args:
            config_path: Path to library_keywords.json file
        """
        if config_path is None:
            # Default path relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(current_dir, '..', 'config', 'library_keywords.json')
        
        self.config_path = config_path
        self.library_keywords = {}
        
        self._load_config()
        
        try:
            from langchain_community.tools import DuckDuckGoSearchRun
            self.search = DuckDuckGoSearchRun()
            self.available = True
        except ImportError:
            print("[DOC_FETCHER] DuckDuckGo search not available")
            self.available = False
    
    def _load_config(self):
        """Load library keywords from JSON file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Convert from detailed format to simple keyword mapping
            libraries = config.get('libraries', {})
            self.library_keywords = {
                lib_name: lib_data['keywords']
                for lib_name, lib_data in libraries.items()
            }
            
            print(f"[DOC_FETCHER] Loaded {len(self.library_keywords)} library definitions from config")
            
        except FileNotFoundError:
            print(f"[DOC_FETCHER] Config file not found: {self.config_path}")
            print("[DOC_FETCHER] Using fallback library keywords")
            self._load_fallback_config()
        except json.JSONDecodeError as e:
            print(f"[DOC_FETCHER] Error parsing config file: {e}")
            print("[DOC_FETCHER] Using fallback library keywords")
            self._load_fallback_config()
    
    def _load_fallback_config(self):
        """Fallback configuration if JSON file is not available"""
        self.library_keywords = {
            "fastapi": ["fastapi", "uvicorn"],
            "django": ["django"],
            "flask": ["flask"],
            "requests": ["requests"],
            "numpy": ["numpy"],
            "pandas": ["pandas"],
        }
    
    def fetch(self, error_msg: str, library: str, error_type: str) -> str:
        """
        Fetch documentation for the error
        
        Args:
            error_msg: Extracted error message
            library: Detected library/framework
            error_type: Type of error
            
        Returns:
            Documentation string
        """
        if not self.available:
            return ""
        
        queries = []
        error_name = error_msg.split(':')[0].strip() if ':' in error_msg else error_type
        
        # Try to generate optimized queries using LLM
        try:
            from .llm_manager import GlobalLLMManager
            from langchain_core.messages import SystemMessage, HumanMessage
            
            llm = GlobalLLMManager().get_llm()
            if llm:
                system_prompt = SystemMessage(
                    content=(
                        "You are an expert search query generator. "
                        "Given an error message and a library context, generate exactly 2 highly optimized "
                        "search queries to find solutions on DuckDuckGo. "
                        "Output ONLY the 2 queries, one per line, with no bullet points, numbers, or extra text."
                    )
                )
                human_prompt = HumanMessage(
                    content=f"Error: {error_msg}\nLibrary: {library}\nError Type: {error_name}"
                )
                
                print("[DOC_FETCHER] Optimizing search queries with LLM...")
                response = llm.invoke([system_prompt, human_prompt])
                content = response.content.strip()
                
                # Parse lines, filtering out empty ones
                llm_queries = [line.strip() for line in content.split('\n') if line.strip()][:2]
                
                # Remove common list artifacts just in case
                import re
                llm_queries = [re.sub(r'^(?:\d+\.|\*|-)\s*', '', q) for q in llm_queries]
                
                if len(llm_queries) >= 1:
                    queries = llm_queries
                    print("[DOC_FETCHER] ✓ Successfully generated optimized queries")
        except Exception as e:
            print(f"[DOC_FETCHER] LLM query optimization failed: {e}")
            
        # Fallback to manual query building if LLM failed or wasn't available
        if not queries:
            print("[DOC_FETCHER] Using fallback search query generation")
            if library:
                key_msg = error_msg.split(':')[-1].strip()[:40] if ':' in error_msg else error_msg[:40]
                queries.append(f"{library} {error_name} {key_msg} solution")
                queries.append(f"{library} {error_name} common causes")
            else:
                key_msg = error_msg.split(':')[-1].strip()[:40] if ':' in error_msg else error_msg[:40]
                queries.append(f"python {error_name} {key_msg} fix")
                if error_name and error_name.lower() != "error":
                    queries.append(f"python {error_name} how to fix")
        
        # Fetch from multiple searches
        all_docs = []
        for i, query in enumerate(queries[:2], 1):  # Limit to 2 queries
            try:
                print(f"[DOC_FETCHER] Search {i}/{min(2, len(queries))}: {query[:70]}...")
                docs = self.search.run(query)
                if docs:
                    all_docs.append(docs)
            except Exception as e:
                print(f"[DOC_FETCHER] Search {i} failed: {e}")
        
        if all_docs:
            combined_docs = "\n\n".join(all_docs)
            filtered_docs = self._filter_relevant_docs(combined_docs, error_msg, library, error_name)
            return filtered_docs[:2500]  # Increased limit for better context
        
        return ""
    
    def extract_error_message(self, context: str) -> str:
        """Extract the actual error message from context"""
        lines = context.split('\n')
        
        # Priority 1: Look for Python error types (most specific)
        error_types = [
            'Error:', 'Exception:', 'Warning:',
            'NameError:', 'TypeError:', 'ValueError:', 'KeyError:', 
            'AttributeError:', 'ImportError:', 'ModuleNotFoundError:',
            'IndexError:', 'ZeroDivisionError:', 'FileNotFoundError:',
            'PermissionError:', 'ConnectionError:', 'TimeoutError:',
            'SyntaxError:', 'IndentationError:'
        ]
        
        for line in lines:
            line = line.strip()
            # Check if line contains a specific error type
            for error_type in error_types:
                if error_type in line:
                    # Extract the error message after the error type
                    if ':' in line:
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            # Return the error type + message
                            error_msg = parts[1].strip()
                            # Get the error type name
                            error_name = parts[0].strip().split()[-1]
                            return f"{error_name}: {error_msg}"
                    return line
        
        # Priority 2: Look for generic error indicators
        for line in lines:
            line = line.strip()
            if any(keyword in line for keyword in ["Error:", "Exception:", "Traceback"]):
                # Avoid URL paths and HTTP status codes
                if not any(skip in line for skip in ["/api/", "HTTP/", "[", "]", "GET", "POST"]):
                    if ":" in line:
                        parts = line.split(":", 1)
                        if len(parts) == 2:
                            return parts[1].strip()
                    return line
        
        # Priority 3: Look for lines with common error patterns
        for line in lines:
            line = line.strip()
            # Skip HTTP logs, timestamps, and paths
            if any(skip in line for skip in ["/api/", "HTTP/", "[", "]", "GET", "POST", "Internal Server"]):
                continue
            # Look for lines with "not defined", "not found", etc.
            if any(pattern in line.lower() for pattern in ["not defined", "not found", "cannot", "unable", "failed"]):
                return line[:100]
        
        # Fallback: return first non-empty, non-log line
        for line in lines:
            line = line.strip()
            if line and not any(skip in line for skip in ["/api/", "HTTP/", "[", "]"]):
                return line[:100]
        
        return "error"
    
    def detect_library(self, context: str) -> str:
        """Detect which library/framework is involved"""
        context_lower = context.lower()
        
        for lib_name, keywords in self.library_keywords.items():
            if any(keyword in context_lower for keyword in keywords):
                return lib_name
        
        # Check for site-packages path
        if "site-packages" in context_lower:
            match = re.search(r'site-packages[/\\]([^/\\]+)', context_lower)
            if match:
                return match.group(1)
        
        return ""
    
    def _filter_relevant_docs(self, docs: str, error_msg: str, library: str, error_name: str = "") -> str:
        """Filter documentation to keep only relevant parts"""
        paragraphs = docs.split('\n')
        relevant_parts = []
        
        # Extract keywords from error message
        error_keywords = error_msg.lower().split()[:8]
        
        # Add error name as a high-priority keyword
        if error_name:
            error_keywords.insert(0, error_name.lower())
        
        # Noise patterns to skip
        noise_patterns = [
            'woocommerce', 'order emails', 'demodulate', 'radios',
            'subscribe', 'newsletter', 'advertisement', 'sponsored',
            'buy now', 'click here', 'learn more', 'get started',
            'sign up', 'free trial', 'pricing', 'download now'
        ]
        
        for para in paragraphs:
            para_lower = para.lower()
            
            # Skip noise/marketing content
            if any(noise in para_lower for noise in noise_patterns):
                continue
            
            # Skip very short paragraphs (likely fragments)
            if len(para.strip()) < 30:
                continue
            
            # Skip paragraphs that are just dates or metadata
            if para.strip().startswith(('Jan ', 'Feb ', 'Mar ', 'Apr ', 'May ', 'Jun ',
                                        'Jul ', 'Aug ', 'Sep ', 'Oct ', 'Nov ', 'Dec ',
                                        '1 ', '2 ', '3 ', '4 ', '5 ', '6 ', '7 ', '8 ', '9 ',
                                        '0 ', '10 ', '11 ', '12 ')):
                continue
            
            score = 0
            
            # High priority: contains error name
            if error_name and error_name.lower() in para_lower:
                score += 5
            
            # High priority: contains multiple error keywords
            keyword_matches = sum(1 for keyword in error_keywords if keyword in para_lower and len(keyword) > 2)
            score += keyword_matches * 2
            
            # Medium priority: contains library name
            if library and library.lower() in para_lower:
                score += 3
            
            # Medium priority: contains solution/technical keywords
            technical_keywords = ["import", "defined", "module", "class", "function", "variable", 
                                 "attribute", "method", "exception", "traceback", "stack"]
            if any(word in para_lower for word in technical_keywords):
                score += 2
            
            # Low priority: contains general solution keywords
            if any(word in para_lower for word in ["fix", "solution", "resolve", "cause", "error"]):
                score += 1
            
            # Only include paragraphs with strong relevance
            if score >= 4:  # Increased threshold from 2 to 4
                relevant_parts.append(para)
        
        # If we have relevant parts, return them
        if relevant_parts:
            filtered = '\n'.join(relevant_parts)
            return filtered
        
        # If filtering was too aggressive, return top scored paragraphs
        # Re-score with lower threshold
        scored_paras = []
        for para in paragraphs:
            para_lower = para.lower()
            if len(para.strip()) < 30:
                continue
            if any(noise in para_lower for noise in noise_patterns):
                continue
            
            score = 0
            if error_name and error_name.lower() in para_lower:
                score += 3
            keyword_matches = sum(1 for keyword in error_keywords if keyword in para_lower)
            score += keyword_matches
            
            if score > 0:
                scored_paras.append((score, para))
        
        # Return top 5 paragraphs by score
        scored_paras.sort(reverse=True, key=lambda x: x[0])
        top_paras = [para for score, para in scored_paras[:5]]
        
        return '\n'.join(top_paras) if top_paras else docs[:1000]


