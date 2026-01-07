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
        """Initialize the LLM"""
        try:
            from langchain_openai import ChatOpenAI
            
            self.llm = ChatOpenAI(
                model=self.config.get("model", "mistralai/mistral-small-3.1-24b-instruct-2503"),
                base_url=self.config.get("base_url", "https://integrate.api.nvidia.com/v1"),
                api_key=self.config.get("api_key", os.environ.get("NVIDIA_API_KEY", "")),
                temperature=self.config.get("temperature", 0.1),
            )
            print("[LLM_CLIENT] LLM initialized successfully")
        except ImportError as e:
            print(f"[LLM_CLIENT] Failed to initialize LLM: {e}")
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
            
            prompt = ChatPromptTemplate.from_template("""Analyze this {error_type} error and provide fixes.

Error:
{error}

Format:
TYPE: <type>
CAUSE: <cause>
FIX1: <fix>
FIX2: <fix>
FIX3: <fix>""")
            
            chain = prompt | self.llm
            response = chain.invoke({
                "error_type": error_type,
                "error": error_context[:500]
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
