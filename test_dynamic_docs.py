"""
Quick test of the enhanced agent with dynamic documentation
"""
import sys
sys.path.insert(0, 'e:/Learning/FastApi_/Ai_log_master')

from ai_logmaster.analyzer import analyze_error

# Test error context (TypeError)
error_context = """
Traceback (most recent call last):
  File "test_type_error.py", line 24, in <module>
    result = calculate_average(data)
  File "test_type_error.py", line 18, in calculate_average
    average = total / "invalid"
TypeError: unsupported operand type(s) for /: 'int' and 'str'
"""

print("Testing dynamic documentation fetching...")
print("=" * 60)
print(error_context)
print("=" * 60)

result = analyze_error(error_context)

print("\n\nRESULT:")
print(f"Type: {result.get('type')}")
print(f"Confidence: {result.get('confidence')}")
print(f"Method: {result.get('method')}")
print(f"Cause: {result.get('cause')}")
print(f"\nFixes:")
for i, fix in enumerate(result.get('fixes', []), 1):
    print(f"  {i}. {fix}")
print(f"\nAPI Calls: {result.get('api_calls_used', 'N/A')}")
