"""
Sample code to fetch documentation for raw error logs using DocumentationFetcher
No AI involvement - just documentation retrieval
"""
from ai_logmaster.core.doc_fetcher import DocumentationFetcher

# Sample raw error log (Django NameError)
error_log = r"""28/Nov/2025 02:01:39] "GET /api/shops/ HTTP/1.1" 200 4192
Internal Server Error: /api/services/categories/
Traceback (most recent call last):
  File "C:\Users\Divyansh\AppData\Local\Programs\Python\Python313\Lib\site-packages\django\core\handlers\exception.py", line 55, in inner
    response = get_response(request)
  File "C:\Users\Divyansh\AppData\Local\Programs\Python\Python313\Lib\site-packages\django\core\handlers\base.py", line 197, in _get_response
    response = wrapped_callback(request, *callback_args, **callback_kwargs)
  File "C:\Users\Divyansh\AppData\Local\Programs\Python\Python313\Lib\site-packages\rest_framework\views.py", line 512, in dispatch
    response = handler(request, *args, **kwargs)
  File "E:\Mendlybackend\shops\views.py", line 105, in categories
    return Response(serializer.data)
           ^^^^^^^^
NameError: name 'Response' is not defined
[28/Nov/2025 02:01:39] "GET /api/services/categories/ HTTP/1.1" 500 95835"""

print("=" * 70)
print("DocumentationFetcher - Standalone Usage Example")
print("=" * 70)

# Step 1: Create DocumentationFetcher instance
doc_fetcher = DocumentationFetcher()
print(f"\n[OK] DocumentationFetcher initialized")
print(f"  - Search available: {doc_fetcher.available}")
print(f"  - Libraries loaded: {len(doc_fetcher.library_keywords)}")

# Step 2: Extract error message from logs
print("\n" + "=" * 70)
print("Step 1: Extract Error Message")
print("=" * 70)
error_message = doc_fetcher.extract_error_message(error_log)
print(f"Extracted error: {error_message}")

# Step 3: Detect library/framework
print("\n" + "=" * 70)
print("Step 2: Detect Library/Framework")
print("=" * 70)
library = doc_fetcher.detect_library(error_log)
print(f"Detected library: {library if library else 'None (using Python)'}")

# Step 4: Fetch documentation
print("\n" + "=" * 70)
print("Step 3: Fetch Documentation")
print("=" * 70)

if doc_fetcher.available:
    # Fetch documentation for the error
    documentation = doc_fetcher.fetch(
        error_msg=error_message,
        library=library,
        error_type="value"  # NameError is a type of value error
    )
    
    if documentation:
        print(f"\n[OK] Fetched {len(documentation)} characters of documentation")
        print("\n" + "-" * 70)
        print("Documentation Preview (first 500 chars):")
        print("-" * 70)
        print(documentation[:500])
        print("...")
        print("-" * 70)
    else:
        print("\n[X] No documentation found")
else:
    print("\n[X] DuckDuckGo search not available")
    print("Install with: pip install duckduckgo-search")

# Example 2: Simple Python error
print("\n\n" + "=" * 70)
print("Example 2: Simple Python TypeError")
print("=" * 70)

simple_error = """
Traceback (most recent call last):
  File "test.py", line 5, in <module>
    result = 10 / "invalid"
TypeError: unsupported operand type(s) for /: 'int' and 'str'
"""

error_msg = doc_fetcher.extract_error_message(simple_error)
lib = doc_fetcher.detect_library(simple_error)

print(f"Error: {error_msg}")
print(f"Library: {lib if lib else 'Python (standard)'}")

if doc_fetcher.available:
    docs = doc_fetcher.fetch(error_msg, lib, "type")
    if docs:
        print(f"\n[OK] Fetched {len(docs)} chars")
        print(f"Preview: {docs[:200]}...")

print("\n" + "=" * 70)
print("Done!")
print("=" * 70)