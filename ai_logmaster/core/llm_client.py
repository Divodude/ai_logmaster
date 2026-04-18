"""
LLM Client - Centralized LLM interactions
"""
import os
import re
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    """Handles all LLM interactions for error analysis"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.llm = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the LLM using Groq"""
        try:
            from langchain_groq import ChatGroq
            
            self.llm = ChatGroq(
                model=self.config.get("model", "llama-3.1-8b-instant"),
                api_key=self.config.get("api_key", os.environ.get("GROQ_API_KEY", "")),
                temperature=self.config.get("temperature", 0.1),
                max_tokens=self.config.get("max_tokens", 1024),
            )
            print("[LLM_CLIENT] Groq LLM initialized successfully")
        except ImportError as e:
            print(f"[LLM_CLIENT] Failed to initialize Groq LLM: {e}")
            self.llm = None
    
    def analyze_with_docs(self, error_context: str, documentation: str) -> Dict:
        """
        Analyze error with documentation context
        
        Args:
            error_context: Error logs
            documentation: Fetched documentation
            
        Returns:
            Analysis result dict
        """
        if not self.llm:
            raise Exception("LLM not available")
        
        try:
            from langchain_core.prompts import ChatPromptTemplate
            
            prompt = ChatPromptTemplate.from_template("""You are a debugging expert. Analyze this error using the documentation.

Documentation Context:
{docs}

Error:
{error}

Provide in this EXACT format:
TYPE: <error type>
CAUSE: <root cause>
FIX1: <specific fix>
FIX2: <alternative fix>
FIX3: <prevention tip>""")
            
            chain = prompt | self.llm
            response = chain.invoke({
                "docs": documentation,
                "error": error_context
            })
            
            result = self._parse_response(response.content)
            result["method"] = "AI + Docs"
            result["confidence"] = 0.90
            
            return result
            
        except Exception as e:
            print(f"[LLM_CLIENT] Analysis with docs failed: {e}")
            raise
    
    def analyze_basic(self, error_context: str, error_type: str = "unknown") -> Dict:
        """
        Basic AI analysis without documentation
        
        Args:
            error_context: Error logs
            error_type: Type of error
            
        Returns:
            Analysis result dict
        """
        if not self.llm:
            raise Exception("LLM not available")
        
        try:
            from langchain_core.prompts import ChatPromptTemplate
            
            prompt = ChatPromptTemplate.from_template("""Analyze this {error_type} error, using the provided CODEBASE CONTEXT if available.

Error context (including codebase):
{error}

Format ONLY in this exact format with no extra text before or after:
TYPE: <type>
CAUSE: <root cause (mention code if available)>
FIX1: <specific fix>
FIX2: <alternative fix>
FIX3: <prevention tip>""")
            
            chain = prompt | self.llm
            response = chain.invoke({
                "error_type": error_type,
                "error": error_context
            })
            
            result = self._parse_response(response.content)
            result["method"] = "AI"
            result["confidence"] = 0.75
            
            return result
            
        except Exception as e:
            print(f"[LLM_CLIENT] Basic analysis failed: {e}")
            raise
    
    def _parse_response(self, content: str) -> Dict:
        """Parse AI response"""
        result = {
            "type": "Unknown",
            "cause": "Not determined",
            "fixes": []
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
