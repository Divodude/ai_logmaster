"""
Error Analyzer - Main orchestrator for error analysis
"""
from typing import Dict, Optional

from .llm_client import LLMClient
from .classifier import ErrorClassifier
from .ingestor import CodebaseIngestor


class ErrorAnalyzer:
    """Main orchestrator for error analysis with fallback chain"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.agent = None
        self.llm_client = LLMClient(config)
        self.classifier = ErrorClassifier()
        self.ingestor = CodebaseIngestor(context_lines_limit=200)
        
        # Try to initialize agentic agent
        try:
            from .agentic_agent import AgenticAgent
            self.agent = AgenticAgent(config)
            print("[ANALYZER] Using agentic AI with tool-calling capabilities")
        except Exception as e:
            print(f"[ANALYZER] Agentic agent initialization failed: {e}")
            # Try old agent as fallback
            try:
                from .agent import Agent
                self.agent = Agent(config)
                print("[ANALYZER] Using standard agent")
            except Exception as e2:
                print(f"[ANALYZER] Standard agent initialization failed: {e2}")
    
    def analyze(self, context: str) -> Dict:
        """
        Analyze error with intelligent fallback chain
        
        Fallback order:
        1. Agentic Agent (AI decides tools) - Most intelligent
        2. Basic AI - Without documentation
        3. Pattern matching - Cached solutions
        
        Args:
            context: Error logs and context
            
        Returns:
            Analysis result dict
        """
        # Fetch codebase context
        codebase_context = self.ingestor.get_codebase_context(context)
        augmented_context = context
        if codebase_context:
            augmented_context = f"{context}\n\n{codebase_context}"
            
        # Try agentic agent first
        if self.agent:
            try:
                result = self.agent.analyze(augmented_context)
                if result.get("api_calls_used") is not None:
                    print(f"[ANALYZER] API calls used: {result['api_calls_used']}")
                return result
            except Exception as e:
                print(f"[ANALYZER] Agent failed: {e}, falling back to basic AI")
        
        # Fallback to basic AI
        try:
            print("[ANALYZER] Using basic AI analysis...")
            error_type, _ = self.classifier.classify(context)
            result = self.llm_client.analyze_basic(augmented_context, error_type)
            return result
        except Exception as e:
            print(f"[ANALYZER] AI analysis failed: {e}, using pattern matching")
        
        # Final fallback to pattern matching
        print("[ANALYZER] Using pattern matching...")
        error_type, _ = self.classifier.classify(context)
        cached = self.classifier.get_cached_solution(error_type)
        return cached or self.classifier.get_generic_solution()

    def attempt_auto_fix(self, context: str, analysis_result: Dict, auto_confirm: bool = False) -> bool:
        """
        Attempt to automatically fix the code using the LLM.
        """
        from .auto_fixer import AutoFixer
        
        llm = None
        # Get the LLM instance from the agent or basic client
        if self.agent and hasattr(self.agent, "llm") and self.agent.llm:
            llm = self.agent.llm
        elif self.llm_client and getattr(self.llm_client, "llm", None):
            llm = self.llm_client.llm
            
        if not llm:
            print("[ANALYZER] No LLM available to perform auto-fix.")
            return False
            
        fixer = AutoFixer(llm=llm)
        files = self.ingestor.get_user_files(context)
        return fixer.attempt_fix(context, analysis_result, files, auto_confirm)


# Backward compatibility function
def analyze_error(context: str) -> Dict:
    """
    Backward compatible wrapper for existing code
    
    Args:
        context: Error logs
        
    Returns:
        Analysis result
    """
    analyzer = ErrorAnalyzer()
    return analyzer.analyze(context)
