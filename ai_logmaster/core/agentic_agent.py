"""
Agentic AI Agent - Direct Groq LLM calls with structured output
Uses ChatGroq directly for fast, reliable analysis without parallel tool call issues
"""
import os
import re
from typing import Optional, Dict
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage, SystemMessage
from .classifier import ErrorClassifier

load_dotenv()


class AgenticAgent:
    """Groq-powered AI agent for error analysis"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.classifier = ErrorClassifier()
        self.llm = None
        self.agent_executor = self  # keep compatibility with analyzer.py check
        
        self._initialize()
    
    def _initialize(self):
        """Initialize the Groq LLM"""
        try:
            from langchain_groq import ChatGroq
            
            self.llm = ChatGroq(
                model=self.config.get("model", "llama-3.1-8b-instant"),
                api_key=self.config.get("api_key", os.environ.get("GROQ_API_KEY", "")),
                temperature=self.config.get("temperature", 0.1),
                max_tokens=self.config.get("max_tokens", 1024),
            )
            print("[AGENTIC_AGENT] Initialized with Groq LLM")
            
        except ImportError as e:
            print(f"[AGENTIC_AGENT] Failed to initialize: {e}")
            self.llm = None
            self.agent_executor = None
        except Exception as e:
            print(f"[AGENTIC_AGENT] Initialization error: {e}")
            self.llm = None
            self.agent_executor = None
    
    def invoke(self, inputs: dict) -> dict:
        """Compatibility shim"""
        return inputs
    
    def analyze(self, error_context: str) -> Dict:
        """
        Analyze error using Groq LLM directly.
        
        Args:
            error_context: Error logs and context
            
        Returns:
            Analysis result dict
        """
        if not self.llm:
            raise Exception("Groq LLM not initialized")
        
        print("[AGENTIC_AGENT] Starting Groq analysis...")
        
        try:
            system = SystemMessage(content="""You are an expert debugging assistant.
Analyze the error and the provided CODEBASE CONTEXT (if any) to provide a specific fix for the user's codebase.
Respond ONLY in this exact format with no extra text before or after:
TYPE: <error type>
CAUSE: <root cause in one sentence (referencing the specific code)>
FIX1: <specific actionable fix (mention the file and line if possible)>
FIX2: <alternative fix>
FIX3: <prevention tip>""")
            
            human = HumanMessage(content=f"Analyze this error and context:\n\n{error_context}")
            
            response = self.llm.invoke([system, human])
            content = response.content
            
            analysis = self._parse_response(content)
            analysis["api_calls_used"] = 1
            analysis["method"] = "Groq AI"
            analysis["confidence"] = 0.88
            
            print("[AGENTIC_AGENT] \u2713 Groq analysis complete")
            return analysis
            
        except Exception as e:
            print(f"[AGENTIC_AGENT] Analysis failed: {e}")
            # Fallback to cached solution
            error_type, _ = self.classifier.classify(error_context)
            cached = self.classifier.get_cached_solution(error_type)
            return cached or self.classifier.get_generic_solution()
    
    def _parse_response(self, content: str) -> Dict:
        """Parse AI response into structured format"""
        result = {
            "type": "Unknown",
            "cause": "Not determined",
            "fixes": [],
            "confidence": 0.88
        }
        
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('TYPE:'):
                result["type"] = line.replace('TYPE:', '').strip()
            elif line.startswith('CAUSE:'):
                result["cause"] = line.replace('CAUSE:', '').strip()
            elif line.startswith('FIX'):
                fix = re.sub(r'^FIX\d+:\s*', '', line)
                if fix:
                    result["fixes"].append(fix)
        
        return result


# Backward compatibility function
def analyze_with_agent(error_context: str) -> Dict:
    """
    Backward compatible wrapper for agentic analysis
    
    Args:
        error_context: Error logs
        
    Returns:
        Analysis result
    """
    try:
        agent = AgenticAgent()
        return agent.analyze(error_context)
    except Exception as e:
        print(f"[AGENT] Agentic analysis failed: {e}")
        classifier = ErrorClassifier()
        error_type, _ = classifier.classify(error_context)
        cached = classifier.get_cached_solution(error_type)
        return cached or classifier.get_generic_solution()
