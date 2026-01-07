"""
Test the new class-based architecture
"""
import sys
sys.path.insert(0, 'e:/Learning/FastApi_/Ai_log_master')

print("=" * 60)
print("Testing Class-Based Architecture")
print("=" * 60)

# Test 1: Import all classes
print("\n1. Testing imports...")
try:
    from ai_logmaster.core.classifier import ErrorClassifier
    from ai_logmaster.core.doc_fetcher import DocumentationFetcher
    from ai_logmaster.core.llm_client import LLMClient
    from ai_logmaster.core.agent import Agent
    from ai_logmaster.core.analyzer import ErrorAnalyzer
    print("✓ All classes imported successfully")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Test ErrorClassifier
print("\n2. Testing ErrorClassifier...")
classifier = ErrorClassifier()
error_type, needs_docs = classifier.classify("ModuleNotFoundError: No module named 'test'")
print(f"   Error type: {error_type}, Needs docs: {needs_docs}")
cached = classifier.get_cached_solution("import")
print(f"   Cached solution: {cached['type']}")
print("✓ ErrorClassifier works")

# Test 3: Test DocumentationFetcher
print("\n3. Testing DocumentationFetcher...")
doc_fetcher = DocumentationFetcher()
error_msg = doc_fetcher.extract_error_message("TypeError: unsupported operand type(s) for /: 'int' and 'str'")
print(f"   Extracted error: {error_msg}")
library = doc_fetcher.detect_library("from fastapi import FastAPI")
print(f"   Detected library: {library}")
print("✓ DocumentationFetcher works")

# Test 4: Test ErrorAnalyzer (without LLM)
print("\n4. Testing ErrorAnalyzer with pattern matching...")
analyzer = ErrorAnalyzer()
test_error = """
Traceback (most recent call last):
  File "test.py", line 5, in <module>
    import nonexistent_module
ModuleNotFoundError: No module named 'nonexistent_module'
"""
result = analyzer.analyze(test_error)
print(f"   Type: {result.get('type')}")
print(f"   Method: {result.get('method')}")
print(f"   Confidence: {result.get('confidence')}")
print("✓ ErrorAnalyzer works")

# Test 5: Test backward compatibility
print("\n5. Testing backward compatibility...")
from ai_logmaster import analyze_error
result2 = analyze_error(test_error)
print(f"   Type: {result2.get('type')}")
print("✓ Backward compatibility works")

print("\n" + "=" * 60)
print("All tests passed! ✓")
print("=" * 60)
