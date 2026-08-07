"""
Unit tests for ErrorClassifier
"""
import unittest
from ai_logmaster.core.classifier import ErrorClassifier


class TestErrorClassifier(unittest.TestCase):

    def setUp(self):
        self.classifier = ErrorClassifier()

    def test_classify_import_error(self):
        log = "ModuleNotFoundError: No module named 'nonexistent_module'"
        error_type, needs_docs = self.classifier.classify(log)
        self.assertEqual(error_type, "import")
        self.assertFalse(needs_docs)

    def test_classify_connection_error(self):
        log = "ConnectionRefusedError: [Errno 111] Connection refused"
        error_type, needs_docs = self.classifier.classify(log)
        self.assertEqual(error_type, "connection")
        self.assertFalse(needs_docs)

    def test_classify_type_error(self):
        log = "TypeError: unsupported operand type(s) for /: 'int' and 'str'"
        error_type, needs_docs = self.classifier.classify(log)
        self.assertEqual(error_type, "type")
        self.assertTrue(needs_docs)

    def test_classify_unknown_error(self):
        log = "CustomAppException: Something completely unexpected happened"
        error_type, needs_docs = self.classifier.classify(log)
        self.assertEqual(error_type, "unknown")
        self.assertTrue(needs_docs)

    def test_get_cached_solution_known(self):
        solution = self.classifier.get_cached_solution("import")
        self.assertIsNotNone(solution)
        self.assertEqual(solution["type"], "Import Error")
        self.assertGreater(len(solution["fixes"]), 0)

    def test_get_cached_solution_unknown(self):
        solution = self.classifier.get_cached_solution("non_existent_key")
        self.assertIsNone(solution)

    def test_get_generic_solution(self):
        solution = self.classifier.get_generic_solution()
        self.assertEqual(solution["type"], "Unknown Error")
        self.assertEqual(solution["confidence"], 0.40)


if __name__ == "__main__":
    unittest.main()
