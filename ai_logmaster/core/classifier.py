"""
Error Classifier - Pattern-based error classification and cached solutions
"""
import json
import os
import re
from typing import Dict, Optional, Tuple


class ErrorClassifier:
    """Classifies errors using pattern matching and provides cached solutions"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize ErrorClassifier
        
        Args:
            config_path: Path to cached_solutions.json file
        """
        if config_path is None:
            # Default path relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(current_dir, '..', 'config', 'cached_solutions.json')
        
        self.config_path = config_path
        self.error_patterns = {}
        self.cached_solutions = {}
        self.generic_solution = {}
        
        self._load_config()
    
    def _load_config(self):
        """Load error patterns and cached solutions from JSON file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.error_patterns = config.get('error_patterns', {})
            self.cached_solutions = config.get('cached_solutions', {})
            self.generic_solution = config.get('generic_solution', {
                "type": "Unknown Error",
                "cause": "Unable to classify",
                "fixes": ["Read error message carefully", "Search error online"],
                "method": "Generic",
                "confidence": 0.40
            })
            
            print(f"[CLASSIFIER] Loaded {len(self.cached_solutions)} cached solutions from config")
            
        except FileNotFoundError:
            print(f"[CLASSIFIER] Config file not found: {self.config_path}")
            print("[CLASSIFIER] Using fallback patterns")
            self._load_fallback_config()
        except json.JSONDecodeError as e:
            print(f"[CLASSIFIER] Error parsing config file: {e}")
            print("[CLASSIFIER] Using fallback patterns")
            self._load_fallback_config()
    
    def _load_fallback_config(self):
        """Fallback configuration if JSON file is not available"""
        self.error_patterns = {
            "connection": ["ConnectionRefused", "Connection refused"],
            "import": ["ModuleNotFoundError", "ImportError"],
            "memory": ["MemoryError", "Out of memory"],
            "timeout": ["TimeoutError", "timed out"],
            "permission": ["PermissionError", "Permission denied"],
            "syntax": ["SyntaxError", "IndentationError"],
            "type": ["TypeError", "AttributeError"],
            "value": ["ValueError", "KeyError"],
        }
        
        self.cached_solutions = {
            "import": {
                "type": "Import Error",
                "cause": "Required package is not installed",
                "fixes": ["Install package: pip install <package-name>"],
                "confidence": 0.80,
                "method": "Cached"
            }
        }
        
        self.generic_solution = {
            "type": "Unknown Error",
            "cause": "Unable to classify",
            "fixes": ["Read error message carefully"],
            "method": "Generic",
            "confidence": 0.40
        }
    
    def classify(self, context: str) -> Tuple[str, bool]:
        """
        Classify error type from context
        
        Args:
            context: Error logs and context
            
        Returns:
            Tuple of (error_type, needs_docs)
        """
        error_type = "unknown"
        
        for err_type, keywords in self.error_patterns.items():
            if any(kw in context for kw in keywords):
                error_type = err_type
                break
        
        # Only fetch docs for complex/uncommon errors
        needs_docs = error_type in ["syntax", "type", "value", "unknown"]
        
        return error_type, needs_docs
    
    def get_cached_solution(self, error_type: str) -> Optional[Dict]:
        """
        Get cached solution for common error types
        
        Args:
            error_type: Type of error
            
        Returns:
            Solution dict or None if not cached
        """
        return self.cached_solutions.get(error_type)
    
    def get_generic_solution(self) -> Dict:
        """Get generic fallback solution"""
        return self.generic_solution.copy()
