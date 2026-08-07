"""
Unit tests for ErrorAnalyzer
"""
import unittest
from ai_logmaster.core.analyzer import ErrorAnalyzer


class TestErrorAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = ErrorAnalyzer()

    def test_analyze_cached_error(self):
        log = """
Traceback (most recent call last):
  File "main.py", line 2, in <module>
    import non_existent_pkg
ModuleNotFoundError: No module named 'non_existent_pkg'
"""
        result = self.analyzer.analyze(log)
        self.assertIsNotNone(result)
        self.assertTrue(result.get("type") == "Import Error" or result.get("method") == "Cached")
        self.assertGreater(len(result.get("fixes", [])), 0)

    def test_analyze_permission_error(self):
        log = "PermissionError: [Errno 13] Permission denied: '/root/test'"
        result = self.analyzer.analyze(log)
        self.assertIsNotNone(result)
        self.assertIn("Permission", result.get("type", ""))


if __name__ == "__main__":
    unittest.main()
