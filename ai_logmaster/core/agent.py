"""
LangGraph Agent for Smart Error Analysis
Uses class-based architecture with dependency injection
"""
import os
from typing import TypedDict, Optional, Dict
from dotenv import load_dotenv

from .classifier import ErrorClassifier
from .doc_fetcher import DocumentationFetcher
from .llm_client import LLMClient
from .error_cache import ErrorCache

load_dotenv()


# State definition
class AgentState(TypedDict):
    error_context: str
    error_type: str
    needs_docs: bool
    documentation: str
    analysis: dict
    api_calls: int
    cache_hit: bool


class Agent:
    """Smart agent for error analysis with API optimization"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.classifier = ErrorClassifier()
        self.doc_fetcher = DocumentationFetcher()
        self.llm_client = LLMClient(config)
        self.error_cache = ErrorCache()
        self.graph = None
        self._initialize_graph()
    
    def _initialize_graph(self):
        """Initialize the LangGraph workflow"""
        try:
            from langgraph.graph import StateGraph, END

            # Build the graph
            workflow = StateGraph(AgentState)

            # Add nodes
            workflow.add_node("cache_lookup", self._cache_lookup)
            workflow.add_node("classify", self._classify_error)
            workflow.add_node("fetch_docs", self._fetch_documentation)
            workflow.add_node("ai_analysis", self._analyze_with_ai)
            workflow.add_node("cache_store", self._cache_store)
            workflow.add_node("cached_solution", self._use_cached_solution)

            # Entry: always try cache first
            workflow.set_entry_point("cache_lookup")

            # Cache hit → done immediately; miss → normal flow
            workflow.add_conditional_edges(
                "cache_lookup",
                self._cache_hit_or_miss,
                {
                    "hit": END,
                    "miss": "classify",
                }
            )
            workflow.add_edge("classify", "fetch_docs")
            workflow.add_conditional_edges(
                "fetch_docs",
                self._should_use_ai,
                {
                    "ai": "ai_analysis",
                    "cached": "cached_solution",
                }
            )
            # After AI analysis → persist to cache → done
            workflow.add_edge("ai_analysis", "cache_store")
            workflow.add_edge("cache_store", END)
            workflow.add_edge("cached_solution", END)

            # Compile
            self.graph = workflow.compile()
            print("[AGENT] LangGraph workflow initialized")

        except ImportError as e:
            print(f"[AGENT] LangGraph not available: {e}")
            self.graph = None
        except Exception as e:
            print(f"[AGENT] Failed to create graph: {e}")
            self.graph = None
    
    def analyze(self, error_context: str) -> Dict:
        """
        Analyze error using the agent workflow
        
        Args:
            error_context: Error logs and context
            
        Returns:
            Analysis result dict
        """
        if not self.graph:
            raise Exception("Agent graph not initialized")
        
        initial_state = {
            "error_context": error_context,
            "error_type": "",
            "needs_docs": False,
            "documentation": "",
            "analysis": {},
            "api_calls": 0,
            "cache_hit": False,
        }
        
        try:
            result = self.graph.invoke(initial_state)
            analysis = result["analysis"]
            analysis["api_calls_used"] = result["api_calls"]
            return analysis
        except Exception as e:
            print(f"[AGENT] Execution failed: {e}")
            raise
    
    def _cache_lookup(self, state: AgentState) -> AgentState:
        """Node: Check the smart error cache before doing any work."""
        cached = self.error_cache.get(state["error_context"])
        if cached:
            fp = cached.get("fingerprint", "?")
            print(f"[CACHE] ✅ HIT! fingerprint={fp} — returning cached AI solution (0 API calls)")
            state["analysis"] = cached
            state["cache_hit"] = True
        else:
            print("[CACHE] Miss — running full analysis pipeline")
            state["cache_hit"] = False
        return state

    def _cache_hit_or_miss(self, state: AgentState) -> str:
        """Decision: was the cache lookup a hit or a miss?"""
        return "hit" if state["cache_hit"] else "miss"

    def _classify_error(self, state: AgentState) -> AgentState:
        """Node: Classify error type"""
        print("[AGENT] Classifying error type...")

        error_type, needs_docs = self.classifier.classify(state["error_context"])

        state["error_type"] = error_type
        state["needs_docs"] = needs_docs
        state["api_calls"] = 0

        print(f"[AGENT] Error type: {error_type}, Needs docs: {needs_docs}")
        return state
    
    def _fetch_documentation(self, state: AgentState) -> AgentState:
        """Node: Fetch documentation if needed"""
        if not state["needs_docs"]:
            print("[AGENT] Using cached knowledge, skipping doc fetch")
            state["documentation"] = ""
            return state
        
        print("[AGENT] Fetching documentation from web...")
        
        error_msg = self.doc_fetcher.extract_error_message(state["error_context"])
        library = self.doc_fetcher.detect_library(state["error_context"])
        
        print(f"[AGENT] Detected error: {error_msg}")
        if library:
            print(f"[AGENT] Detected library/framework: {library}")
        
        docs = self.doc_fetcher.fetch(error_msg, library, state["error_type"])
        state["documentation"] = docs
        
        if docs:
            print(f"[AGENT] [OK] Fetched {len(docs)} chars of documentation")
        else:
            print("[AGENT] [X] No documentation found")
        
        return state
    
    def _analyze_with_ai(self, state: AgentState) -> AgentState:
        """Node: Use AI for analysis"""
        print("[AGENT] Analyzing with AI...")
        
        try:
            if state["documentation"]:
                analysis = self.llm_client.analyze_with_docs(
                    state["error_context"],
                    state["documentation"]
                )
            else:
                analysis = self.llm_client.analyze_basic(
                    state["error_context"],
                    state["error_type"]
                )
            
            state["analysis"] = analysis
            state["api_calls"] += 1
            
            print(f"[AGENT] [OK] Analysis complete (API calls: {state['api_calls']})")
            
        except Exception as e:
            print(f"[AGENT] AI analysis failed: {e}")
            # Fallback to cached or generic
            cached = self.classifier.get_cached_solution(state["error_type"])
            state["analysis"] = cached or self.classifier.get_generic_solution()
        
        return state
    
    def _cache_store(self, state: AgentState) -> AgentState:
        """Node: Persist the AI result to the error cache for future hits."""
        if state.get("analysis") and not state.get("cache_hit"):
            fp = self.error_cache.store(state["error_context"], state["analysis"])
            print(f"[CACHE] 💾 Stored AI solution → fingerprint={fp}")
        return state

    def _use_cached_solution(self, state: AgentState) -> AgentState:
        """Node: Use static fallback solution (last resort — no AI, no cache hit)."""
        print("[AGENT] Using static fallback solution...")

        fallback = self.classifier.get_cached_solution(state["error_type"])
        if fallback:
            state["analysis"] = fallback
            print(f"[AGENT] [OK] Using static fallback for {state['error_type']}")
        else:
            state["analysis"] = self.classifier.get_generic_solution()
            print("[AGENT] [OK] Using generic solution")

        return state

    def _should_use_ai(self, state: AgentState) -> str:
        """Decision: Should we use AI or static fallback?"""
        if state["needs_docs"] or state["error_type"] == "unknown":
            return "ai"
        return "cached"


# Backward compatibility function
def analyze_with_agent(error_context: str) -> Dict:
    """
    Backward compatible wrapper for existing code
    
    Args:
        error_context: Error logs
        
    Returns:
        Analysis result
    """
    try:
        agent = Agent()
        return agent.analyze(error_context)
    except Exception as e:
        print(f"[AGENT] Failed: {e}")
        # Fallback
        classifier = ErrorClassifier()
        return classifier.get_generic_solution()
