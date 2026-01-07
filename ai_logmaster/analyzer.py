"""
AI-Powered Error Analyzer with RAG
Uses LangChain, Vector Store, and Documentation Retrieval for precise solutions
"""
import os
import re
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

# RAG Components
_vector_store = None
_retriever = None

def initialize_rag():
    """Initialize RAG system with documentation"""
    global _vector_store, _retriever
    
    if _retriever is not None:
        return  # Already initialized
    
    try:
        from langchain_community.document_loaders import WebBaseLoader
        from langchain_community.vectorstores import FAISS
        from langchain_openai import OpenAIEmbeddings
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        
        print("[RAG] Initializing documentation retrieval system...")
        
        # Common documentation URLs
        docs_urls = [
            # Python
            "https://docs.python.org/3/library/exceptions.html",
            # FastAPI
            "https://fastapi.tiangolo.com/tutorial/debugging/",
            # Requests
            "https://requests.readthedocs.io/en/latest/user/quickstart/",
            # Add more as needed
        ]
        
        # Load documents
        print("[RAG] Loading documentation...")
        all_docs = []
        for url in docs_urls:
            try:
                loader = WebBaseLoader(url)
                docs = loader.load()
                all_docs.extend(docs)
                print(f"[RAG] ✓ Loaded: {url}")
            except Exception as e:
                print(f"[RAG] ✗ Failed to load {url}: {e}")
        
        if not all_docs:
            print("[RAG] No documents loaded, using fallback mode")
            return
        
        # Split documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        splits = text_splitter.split_documents(all_docs)
        print(f"[RAG] Created {len(splits)} document chunks")
        
        # Create embeddings and vector store
        print("[RAG] Creating embeddings...")
        embeddings = OpenAIEmbeddings(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=os.environ.get("NVIDIA_API_KEY", "")
        )
        
        _vector_store = FAISS.from_documents(splits, embeddings)
        _retriever = _vector_store.as_retriever(search_kwargs={"k": 3})
        
        print("[RAG] ✓ RAG system initialized successfully!")
        
    except ImportError as e:
        print(f"[RAG] Missing dependencies: {e}")
        print("[RAG] Install with: pip install langchain langchain-community faiss-cpu")
    except Exception as e:
        print(f"[RAG] Initialization failed: {e}")

def analyze_error(context: str) -> Dict:
    """
    Analyze error context using LangGraph agent (optimized for API quota)
    
    Args:
        context: Error logs and surrounding context
        
    Returns:
        Dictionary with error type, confidence, fixes, and documentation references
    """
    
    # Try LangGraph agent first (most optimized)
    try:
        from .agent import analyze_with_agent
        print("[ANALYZER] Using LangGraph agent...")
        result = analyze_with_agent(context)
        if result.get("api_calls_used") is not None:
            print(f"[ANALYZER] API calls used: {result['api_calls_used']}")
        return result
    except ImportError as e:
        print(f"[ANALYZER] LangGraph agent not available: {e}, falling back to RAG")
    except Exception as e:
        print(f"[ANALYZER] Agent failed: {e}, falling back to RAG")
    
    # Fallback to RAG
    initialize_rag()
    if _retriever is not None:
        return rag_analysis(context)
    
    # Fallback to basic AI
    try:
        return ai_analysis(context)
    except Exception as e:
        print(f"[ANALYZER] AI analysis failed: {e}")
        return fallback_analysis(context)

def rag_analysis(context: str) -> Dict:
    """RAG-enhanced error analysis with documentation retrieval"""
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.runnables import RunnablePassthrough
        from langchain_core.output_parsers import StrOutputParser
        
        print("[RAG] Retrieving relevant documentation...")
        
        # Retrieve relevant docs
        docs = _retriever.invoke(context)
        doc_context = "\n\n".join([doc.page_content for doc in docs])
        
        print(f"[RAG] Found {len(docs)} relevant documentation sections")
        
        # Initialize LLM
        llm = ChatOpenAI(
            model="mistralai/mistral-small-3.1-24b-instruct-2503",
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=os.environ.get("NVIDIA_API_KEY", ""),
            temperature=0.2,
        )
        
        # Create RAG prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert software debugger with access to official documentation.

Analyze the error using the provided documentation context and error logs.

Provide:
1. Error type (concise, e.g., "Database Connection Error")
2. Root cause based on documentation
3. 3-5 specific fixes with documentation references

Format your response EXACTLY as:
TYPE: <error type>
CAUSE: <root cause explanation>
FIX1: <first fix with reference>
FIX2: <second fix with reference>
FIX3: <third fix with reference>
DOCS: <relevant documentation URLs or sections>
"""),
            ("user", """Documentation Context:
{doc_context}

Error Logs:
{error_context}

Analyze and provide solutions:""")
        ])
        
        # Create chain
        chain = (
            {"doc_context": lambda x: doc_context, "error_context": lambda x: x}
            | prompt
            | llm
            | StrOutputParser()
        )
        
        # Get response
        response = chain.invoke(context)
        
        # Parse response
        result = parse_ai_response(response)
        result['confidence'] = 0.90  # Higher confidence with RAG
        result['method'] = 'RAG'
        
        # Add documentation sources
        result['sources'] = [doc.metadata.get('source', 'Unknown') for doc in docs]
        
        return result
        
    except Exception as e:
        print(f"[RAG] Analysis failed: {e}")
        return ai_analysis(context)

def ai_analysis(context: str) -> Dict:
    """Basic AI analysis without RAG"""
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate
        
        llm = ChatOpenAI(
            model="mistralai/mistral-small-3.1-24b-instruct-2503",
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=os.environ.get("NVIDIA_API_KEY", ""),
            temperature=0.2,
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert software debugger. Analyze the error logs and provide:
1. Error type (concise)
2. Root cause explanation
3. 3-5 specific, actionable fixes

Format your response as:
TYPE: <error type>
CAUSE: <root cause>
FIX1: <first fix>
FIX2: <second fix>
FIX3: <third fix>
"""),
            ("user", "Error logs:\n{context}")
        ])
        
        chain = prompt | llm
        response = chain.invoke({"context": context})
        
        result = parse_ai_response(response.content)
        result['confidence'] = 0.75
        result['method'] = 'AI'
        
        return result
        
    except Exception as e:
        print(f"[AI] Analysis failed: {e}")
        return fallback_analysis(context)

def parse_ai_response(content: str) -> Dict:
    """Parse structured AI response"""
    lines = content.split('\n')
    result = {
        'type': 'Unknown Error',
        'cause': 'Could not determine',
        'fixes': [],
        'docs': []
    }
    
    for line in lines:
        line = line.strip()
        if line.startswith('TYPE:'):
            result['type'] = line.replace('TYPE:', '').strip()
        elif line.startswith('CAUSE:'):
            result['cause'] = line.replace('CAUSE:', '').strip()
        elif line.startswith('FIX'):
            fix = re.sub(r'^FIX\d+:\s*', '', line)
            if fix:
                result['fixes'].append(fix)
        elif line.startswith('DOCS:'):
            docs = line.replace('DOCS:', '').strip()
            result['docs'] = [d.strip() for d in docs.split(',') if d.strip()]
    
    return result

def fallback_analysis(context: str) -> Dict:
    """Fallback pattern-based analysis"""
    
    patterns = {
        r"ConnectionRefused|Connection refused": {
            'type': 'Connection Refused',
            'cause': 'Unable to establish connection to the target service',
            'fixes': [
                'Check if the service is running (e.g., systemctl status <service>)',
                'Verify the host and port are correct in your configuration',
                'Check firewall settings and network connectivity',
                'Ensure the service is listening on the correct interface'
            ]
        },
        r"ModuleNotFoundError|ImportError": {
            'type': 'Missing Module',
            'cause': 'Required Python package is not installed',
            'fixes': [
                'Install the missing package: pip install <package-name>',
                'Check your virtual environment is activated',
                'Verify package name spelling in requirements.txt',
                'Update pip: python -m pip install --upgrade pip'
            ]
        },
        r"MemoryError|Out of memory": {
            'type': 'Out of Memory',
            'cause': 'Application exceeded available system memory',
            'fixes': [
                'Reduce batch size or data volume being processed',
                'Increase system memory or use swap space',
                'Optimize memory usage (use generators, del unused objects)',
                'Profile memory usage with memory_profiler'
            ]
        },
        r"TimeoutError|timed out|Read timed out": {
            'type': 'Timeout Error',
            'cause': 'Operation exceeded the configured timeout duration',
            'fixes': [
                'Increase timeout duration in your configuration',
                'Check network connectivity and latency',
                'Optimize slow operations (database queries, API calls)',
                'Implement retry logic with exponential backoff'
            ]
        },
        r"PermissionError|Permission denied": {
            'type': 'Permission Denied',
            'cause': 'Insufficient permissions to access file/resource',
            'fixes': [
                'Check file/directory permissions: ls -la <path>',
                'Run with appropriate privileges (sudo if needed)',
                'Verify user has access rights to the resource',
                'Check SELinux/AppArmor policies if applicable'
            ]
        }
    }
    
    for pattern, info in patterns.items():
        if re.search(pattern, context, re.IGNORECASE):
            return {
                'type': info['type'],
                'cause': info['cause'],
                'confidence': 0.70,
                'fixes': info['fixes'],
                'method': 'Pattern'
            }
    
    return {
        'type': 'Unknown Error',
        'cause': 'Unable to classify error automatically',
        'confidence': 0.30,
        'fixes': [
            'Read the error message and stack trace carefully',
            'Search for the error message online',
            'Check recent code changes that might have introduced the issue',
            'Review application logs for additional context',
            'Consult the official documentation for the library/framework'
        ],
        'method': 'Generic'
    }
