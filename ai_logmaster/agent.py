"""
LangGraph Agent for Smart Error Analysis
- Decides when to fetch documentation vs use cached knowledge
- Optimizes API usage to stay within free quotas
- Uses DuckDuckGo search for documentation when needed
"""
import os
from typing import TypedDict, Annotated, Literal
from dotenv import load_dotenv

load_dotenv()

# State definition
class AgentState(TypedDict):
    error_context: str
    error_type: str
    needs_docs: bool
    documentation: str
    analysis: dict
    api_calls: int

def create_agent():
    """Create the LangGraph agent"""
    try:
        from langgraph.graph import StateGraph, END
        from langchain_openai import ChatOpenAI
        from langchain_community.tools import DuckDuckGoSearchRun
        from langchain_core.prompts import ChatPromptTemplate
        
        # Initialize LLM (we'll use it sparingly)
        llm = ChatOpenAI(
            model="mistralai/mistral-small-3.1-24b-instruct-2503",
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=os.environ.get("NVIDIA_API_KEY", ""),
            temperature=0.1,  # Lower temperature for consistency
        )
        
        # Initialize search tool
        search = DuckDuckGoSearchRun()
        
        # Node 1: Classify Error (Pattern-based, no API call)
        def classify_error(state: AgentState) -> AgentState:
            """Classify error type using pattern matching (free)"""
            print("[AGENT] Classifying error type...")
            
            context = state["error_context"]
            error_type = "unknown"
            needs_docs = False
            
            # Pattern-based classification (no API needed)
            patterns = {
                "connection": ["ConnectionRefused", "Connection refused", "ECONNREFUSED"],
                "import": ["ModuleNotFoundError", "ImportError", "No module named"],
                "memory": ["MemoryError", "Out of memory", "OOM"],
                "timeout": ["TimeoutError", "timed out", "Read timed out"],
                "permission": ["PermissionError", "Permission denied"],
                "syntax": ["SyntaxError", "IndentationError"],
                "type": ["TypeError", "AttributeError"],
                "value": ["ValueError", "KeyError"],
            }
            
            for err_type, keywords in patterns.items():
                if any(kw in context for kw in keywords):
                    error_type = err_type
                    # Only fetch docs for complex/uncommon errors
                    needs_docs = err_type in ["syntax", "type", "value", "unknown"]
                    break
            
            state["error_type"] = error_type
            state["needs_docs"] = needs_docs
            state["api_calls"] = 0
            
            print(f"[AGENT] Error type: {error_type}, Needs docs: {needs_docs}")
            return state
        
        # Node 2: Fetch Documentation (conditional)
        def fetch_documentation(state: AgentState) -> AgentState:
            """Fetch relevant documentation if needed"""
            if not state["needs_docs"]:
                print("[AGENT] Using cached knowledge, skipping doc fetch")
                state["documentation"] = ""
                return state
            
            print("[AGENT] Fetching documentation from web...")
            
            # Extract error message for search
            lines = state["error_context"].split('\n')
            error_msg = ""
            for line in lines:
                if "Error:" in line or "Exception:" in line:
                    error_msg = line.strip()
                    break
            
            if not error_msg:
                error_msg = f"{state['error_type']} error python"
            
            try:
                # Search for documentation
                query = f"{error_msg} official documentation solution"
                docs = search.run(query)
                state["documentation"] = docs[:1000]  # Limit to 1000 chars
                print(f"[AGENT] ✓ Fetched {len(docs)} chars of documentation")
            except Exception as e:
                print(f"[AGENT] ✗ Doc fetch failed: {e}")
                state["documentation"] = ""
            
            return state
        
        # Node 3: Analyze with AI (only if needed)
        def analyze_with_ai(state: AgentState) -> AgentState:
            """Use AI for analysis (costs API calls)"""
            print("[AGENT] Analyzing with AI...")
            
            # Build context-aware prompt
            if state["documentation"]:
                prompt_template = """You are a debugging expert. Analyze this error using the documentation.

Documentation Context:
{docs}

Error:
{error}

Provide in this EXACT format:
TYPE: <error type>
CAUSE: <root cause>
FIX1: <specific fix>
FIX2: <alternative fix>
FIX3: <prevention tip>"""
                
                prompt = ChatPromptTemplate.from_template(prompt_template)
                chain = prompt | llm
                
                response = chain.invoke({
                    "docs": state["documentation"],
                    "error": state["error_context"]
                })
            else:
                # Simpler prompt for known errors
                prompt_template = """Analyze this {error_type} error and provide fixes.

Error:
{error}

Format:
TYPE: <type>
CAUSE: <cause>
FIX1: <fix>
FIX2: <fix>
FIX3: <fix>"""
                
                prompt = ChatPromptTemplate.from_template(prompt_template)
                chain = prompt | llm
                
                response = chain.invoke({
                    "error_type": state["error_type"],
                    "error": state["error_context"][:500]  # Limit context to save tokens
                })
            
            # Parse response
            content = response.content
            analysis = parse_response(content)
            analysis["method"] = "AI + Docs" if state["documentation"] else "AI"
            analysis["confidence"] = 0.90 if state["documentation"] else 0.75
            
            state["analysis"] = analysis
            state["api_calls"] += 1
            
            print(f"[AGENT] ✓ Analysis complete (API calls: {state['api_calls']})")
            return state
        
        # Node 4: Use Cached Solution (no API call)
        def use_cached_solution(state: AgentState) -> AgentState:
            """Use pre-defined solutions for common errors"""
            print("[AGENT] Using cached solution...")
            
            solutions = {
                "connection": {
                    "type": "Connection Error",
                    "cause": "Service is not running or unreachable",
                    "fixes": [
                        "Check if the service is running",
                        "Verify host and port configuration",
                        "Check firewall and network settings"
                    ]
                },
                "import": {
                    "type": "Import Error",
                    "cause": "Required package is not installed",
                    "fixes": [
                        "Install package: pip install <package-name>",
                        "Activate virtual environment",
                        "Check package name spelling"
                    ]
                },
                "memory": {
                    "type": "Memory Error",
                    "cause": "Insufficient memory available",
                    "fixes": [
                        "Reduce batch size or data volume",
                        "Use generators instead of lists",
                        "Increase system memory"
                    ]
                },
                "timeout": {
                    "type": "Timeout Error",
                    "cause": "Operation took too long",
                    "fixes": [
                        "Increase timeout value",
                        "Optimize slow operations",
                        "Check network latency"
                    ]
                },
                "permission": {
                    "type": "Permission Error",
                    "cause": "Insufficient file/resource permissions",
                    "fixes": [
                        "Check file permissions: ls -la",
                        "Run with appropriate privileges",
                        "Verify user access rights"
                    ]
                }
            }
            
            error_type = state["error_type"]
            if error_type in solutions:
                state["analysis"] = {
                    **solutions[error_type],
                    "method": "Cached",
                    "confidence": 0.80
                }
            else:
                # Fallback
                state["analysis"] = {
                    "type": "Unknown Error",
                    "cause": "Unable to classify",
                    "fixes": [
                        "Read error message carefully",
                        "Search error online",
                        "Check recent code changes"
                    ],
                    "method": "Generic",
                    "confidence": 0.40
                }
            
            print(f"[AGENT] ✓ Using cached solution for {error_type}")
            return state
        
        # Decision function: Should we use AI?
        def should_use_ai(state: AgentState) -> Literal["ai", "cached"]:
            """Decide whether to use AI or cached solution"""
            # Use AI only for complex/unknown errors or when docs are available
            if state["needs_docs"] or state["error_type"] == "unknown":
                return "ai"
            return "cached"
        
        # Build the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("classify", classify_error)
        workflow.add_node("fetch_docs", fetch_documentation)
        workflow.add_node("ai_analysis", analyze_with_ai)
        workflow.add_node("cached_solution", use_cached_solution)
        
        # Add edges
        workflow.set_entry_point("classify")
        workflow.add_edge("classify", "fetch_docs")
        workflow.add_conditional_edges(
            "fetch_docs",
            should_use_ai,
            {
                "ai": "ai_analysis",
                "cached": "cached_solution"
            }
        )
        workflow.add_edge("ai_analysis", END)
        workflow.add_edge("cached_solution", END)
        
        # Compile
        app = workflow.compile()
        
        print("[AGENT] ✓ LangGraph agent initialized")
        return app
        
    except Exception as e:
        print(f"[AGENT] Failed to create agent: {e}")
        return None

def parse_response(content: str) -> dict:
    """Parse AI response"""
    import re
    
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

# Global agent instance
_agent = None

def analyze_with_agent(error_context: str) -> dict:
    """Analyze error using LangGraph agent"""
    global _agent
    
    if _agent is None:
        _agent = create_agent()
    
    if _agent is None:
        # Fallback if agent creation failed
        return {
            "type": "Error",
            "cause": "Agent initialization failed",
            "fixes": ["Check dependencies", "Review error logs"],
            "method": "Fallback",
            "confidence": 0.30
        }
    
    # Run the agent
    initial_state = {
        "error_context": error_context,
        "error_type": "",
        "needs_docs": False,
        "documentation": "",
        "analysis": {},
        "api_calls": 0
    }
    
    try:
        result = _agent.invoke(initial_state)
        analysis = result["analysis"]
        analysis["api_calls_used"] = result["api_calls"]
        return analysis
    except Exception as e:
        print(f"[AGENT] Execution failed: {e}")
        return {
            "type": "Analysis Error",
            "cause": str(e),
            "fixes": ["Check agent configuration"],
            "method": "Error",
            "confidence": 0.20
        }
