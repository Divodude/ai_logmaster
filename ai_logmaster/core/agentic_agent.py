"""
Agentic AI Agent - True tool-calling agent with LangGraph
Uses ReAct pattern where AI decides when to use tools
"""
import os
from typing import TypedDict, Optional, Dict, Annotated, Sequence
from dotenv import load_dotenv

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from .tools import AGENT_TOOLS
from .classifier import ErrorClassifier

load_dotenv()


class AgentState(TypedDict):
    """State for the agentic workflow"""
    messages: Annotated[Sequence[BaseMessage], "The messages in the conversation"]
    error_context: str
    final_analysis: Optional[Dict]


class AgenticAgent:
    """True agentic AI that decides when to use tools"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.classifier = ErrorClassifier()
        self.llm = None
        self.tools = AGENT_TOOLS
        self.agent_executor = None
        
        self._initialize()
    
    def _initialize(self):
        """Initialize the LLM and agent"""
        try:
            from langchain_openai import ChatOpenAI
            from langgraph.prebuilt import create_react_agent
            
            # Initialize LLM
            self.llm = ChatOpenAI(
                model=self.config.get("model", "mistralai/mistral-small-3.1-24b-instruct-2503"),
                base_url=self.config.get("base_url", "https://integrate.api.nvidia.com/v1"),
                api_key=self.config.get("api_key", os.environ.get("NVIDIA_API_KEY", "")),
                temperature=self.config.get("temperature", 0.1),
            )
            
            # Store system prompt to use when invoking
            self.system_prompt = """You are an expert debugging assistant that helps analyze and fix programming errors.

Your goal is to:
1. Understand the error from the context
2. Decide which tools to use (if any) to gather more information
3. Provide a clear, actionable solution

Available tools:
- search_documentation: Search for docs when you need specific information about an error
- get_cached_solution: Get known solutions for common errors (ImportError, ConnectionError, etc.)
- detect_library_from_error: Identify which library/framework is involved
- classify_error_type: Understand the error category

Guidelines:
- For SIMPLE errors (ImportError, ConnectionError): Use get_cached_solution
- For COMPLEX errors (NameError, TypeError with unclear cause): Use search_documentation
- Always detect the library first if you're unsure what framework is involved
- Be concise and provide actionable fixes
- Only use tools when necessary - use your knowledge for obvious errors

Output format:
TYPE: <error type>
CAUSE: <root cause>
FIX1: <first fix>
FIX2: <second fix>
FIX3: <third fix>"""
            
            # Create ReAct agent (no prompt parameter)
            self.agent_executor = create_react_agent(
                self.llm,
                self.tools
            )
            
            print("[AGENTIC_AGENT] Initialized with tool-calling capabilities")
            
        except ImportError as e:
            print(f"[AGENTIC_AGENT] Failed to initialize: {e}")
            self.agent_executor = None
        except Exception as e:
            print(f"[AGENTIC_AGENT] Initialization error: {e}")
            self.agent_executor = None
    
    def analyze(self, error_context: str) -> Dict:
        """
        Analyze error using agentic AI with tools
        
        Args:
            error_context: Error logs and context
            
        Returns:
            Analysis result dict
        """
        if not self.agent_executor:
            raise Exception("Agent not initialized")
        
        print("[AGENTIC_AGENT] Starting agentic analysis...")
        
        try:
            from langchain_core.messages import SystemMessage
            
            # Create messages with system prompt first
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(
                    content=f"""Analyze this error and provide a solution:

{error_context}

Use tools if needed to gather information, then provide your analysis."""
                )
            ]
            
            # Run the agent
            result = self.agent_executor.invoke({
                "messages": messages
            })
            
            # Extract the final AI message
            result_messages = result.get("messages", [])
            final_message = None
            
            for msg in reversed(result_messages):
                if isinstance(msg, AIMessage) and not msg.tool_calls:
                    final_message = msg.content
                    break
            
            if not final_message:
                final_message = result_messages[-1].content if result_messages else "No response"
            
            # Parse the response
            analysis = self._parse_response(final_message)
            
            # Count tool calls (API calls)
            tool_calls = sum(1 for msg in result_messages if isinstance(msg, AIMessage) and msg.tool_calls)
            analysis["api_calls_used"] = tool_calls + 1  # +1 for final response
            analysis["method"] = "Agentic AI"
            
            print(f"[AGENTIC_AGENT] ✓ Analysis complete (Tool calls: {tool_calls}, Total API: {analysis['api_calls_used']})")
            
            return analysis
            
        except Exception as e:
            print(f"[AGENTIC_AGENT] Analysis failed: {e}")
            import traceback
            traceback.print_exc()
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
            "confidence": 0.85
        }
        
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('TYPE:'):
                result["type"] = line.replace('TYPE:', '').strip()
            elif line.startswith('CAUSE:'):
                result["cause"] = line.replace('CAUSE:', '').strip()
            elif line.startswith('FIX'):
                import re
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
        # Fallback
        classifier = ErrorClassifier()
        error_type, _ = classifier.classify(error_context)
        cached = classifier.get_cached_solution(error_type)
        return cached or classifier.get_generic_solution()
