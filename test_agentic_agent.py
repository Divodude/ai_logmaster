"""
Test the new Agentic AI Agent
"""
import sys
sys.path.insert(0, 'e:/Learning/FastApi_/Ai_log_master')

print("=" * 70)
print("Testing Agentic AI Agent with Tool Binding")
print("=" * 70)

# Test 1: Simple ImportError (should use cached solution, no doc search)
print("\n" + "=" * 70)
print("Test 1: Simple ImportError (Should use get_cached_solution)")
print("=" * 70)

simple_error = """
Traceback (most recent call last):
  File "test.py", line 5, in <module>
    import nonexistent_module
ModuleNotFoundError: No module named 'nonexistent_module'
"""

try:
    from ai_logmaster.core.agentic_agent import AgenticAgent
    
    agent = AgenticAgent()
    print("\n[TEST] Analyzing simple ImportError...")
    result = agent.analyze(simple_error)
    
    print(f"\nType: {result.get('type')}")
    print(f"Method: {result.get('method')}")
    print(f"API Calls: {result.get('api_calls_used', 0)}")
    print(f"Fixes: {result.get('fixes', [])[:2]}")
    
except Exception as e:
    print(f"\n✗ Test 1 failed: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Complex NameError (should search documentation)
print("\n\n" + "=" * 70)
print("Test 2: Complex NameError (Should use search_documentation)")
print("=" * 70)

complex_error = """
Traceback (most recent call last):
  File "E:\\Mendlybackend\\shops\\views.py", line 105, in categories
    return Response(serializer.data)
NameError: name 'Response' is not defined
"""

try:
    agent2 = AgenticAgent()
    print("\n[TEST] Analyzing complex NameError...")
    result2 = agent2.analyze(complex_error)
    
    print(f"\nType: {result2.get('type')}")
    print(f"Method: {result2.get('method')}")
    print(f"API Calls: {result2.get('api_calls_used', 0)}")
    print(f"Fixes: {result2.get('fixes', [])[:2]}")
    
except Exception as e:
    print(f"\n✗ Test 2 failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("Tests Complete!")
print("=" * 70)
