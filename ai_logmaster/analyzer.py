"""
AI-Powered Error Analyzer with RAG
Uses LangChain, Vector Store, and Documentation Retrieval for precise solutions
"""
import os
import re
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()



class Analyzer:
    def __init__(self):
        pass
    def analyze_error(self,context: str) -> Dict:
        """
        Analyze error context using intelligent agent with dynamic documentation fetching
        
        Args:
            context: Error logs and surrounding context
            
        Returns:
            Dictionary with error type, confidence, fixes, and documentation references
        """
        
        try:
            from .agent import analyze_with_agent
            print("[ANALYZER] Using LangGraph agent with dynamic documentation...")
            result = analyze_with_agent(context)
            if result.get("api_calls_used") is not None:
                print(f"[ANALYZER] API calls used: {result['api_calls_used']}")
            return result
        except ImportError as e:
            print(f"[ANALYZER] LangGraph agent not available: {e}, falling back to basic AI")
        except Exception as e:
            print(f"[ANALYZER] Agent failed: {e}, falling back to basic AI")
        
        try:
            return ai_analysis(context)
        except Exception as e:
            print(f"[ANALYZER] AI analysis failed: {e}, using pattern matching")
            return fallback_analysis(context)



    def ai_analysis(self,context: str) -> Dict:
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

    def parse_ai_response(self,content: str) -> Dict:
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

    def fallback_analysis(self,context: str) -> Dict:
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
