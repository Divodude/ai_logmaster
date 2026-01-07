"""
Test improved DocumentationFetcher
"""
from ai_logmaster.core.doc_fetcher import DocumentationFetcher

# Django NameError example
django_error = r"""
Internal Server Error: /api/services/categories/
Traceback (most recent call last):
  File "E:\Mendlybackend\shops\views.py", line 105, in categories
    return Response(serializer.data)
NameError: name 'Response' is not defined
"""

print("=" * 70)
print("Testing Improved DocumentationFetcher")
print("=" * 70)

doc_fetcher = DocumentationFetcher()

# Test error extraction
print("\n1. Error Extraction:")
error_msg = doc_fetcher.extract_error_message(django_error)
print(f"   Extracted: '{error_msg}'")

# Test library detection
print("\n2. Library Detection:")
library = doc_fetcher.detect_library(django_error)
print(f"   Detected: '{library}'")

# Test documentation fetching
print("\n3. Documentation Fetching:")
if doc_fetcher.available:
    docs = doc_fetcher.fetch(error_msg, library, "value")
    if docs:
        print(f"   ✓ Fetched {len(docs)} chars")
        print(f"\n   Preview (first 400 chars):")
        print(f"   {'-' * 66}")
        print(f"   {docs[:400]}")
        print(f"   ...")
    else:
        print("   ✗ No docs found")
else:
    print("   ✗ Search not available")

print("\n" + "=" * 70)
