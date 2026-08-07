"""
Unit tests for DocumentationFetcher
"""
import unittest
from ai_logmaster.core.doc_fetcher import DocumentationFetcher


class TestDocumentationFetcher(unittest.TestCase):

    def setUp(self):
        self.doc_fetcher = DocumentationFetcher()

    def test_detect_library_fastapi(self):
        log = "from fastapi import FastAPI\napp = FastAPI()"
        library = self.doc_fetcher.detect_library(log)
        self.assertEqual(library, "fastapi")

    def test_detect_library_django(self):
        log = "File 'django/core/handlers/exception.py'\nNameError: name 'Response' is not defined"
        library = self.doc_fetcher.detect_library(log)
        self.assertEqual(library, "django")

    def test_detect_library_none(self):
        log = "ValueError: invalid literal for int() with base 10: 'abc'"
        library = self.doc_fetcher.detect_library(log)
        self.assertFalse(library)

    def test_extract_error_message(self):
        log = """
Traceback (most recent call last):
  File "test.py", line 5, in <module>
    result = 10 / 0
ZeroDivisionError: division by zero
"""
        error_msg = self.doc_fetcher.extract_error_message(log)
        self.assertIn("ZeroDivisionError: division by zero", error_msg)


if __name__ == "__main__":
    unittest.main()
